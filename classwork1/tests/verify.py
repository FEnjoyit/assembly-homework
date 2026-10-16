"""Compile and test the DOS programs using the shared Windows course environment."""
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--course-root', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    course = args.course_root.resolve()
    work, tests = course/'dos/work', course/'dos/tests/C1'
    tests.mkdir(parents=True, exist_ok=True)
    for p in (HERE/'src').iterdir():
        if p.suffix in ('.ASM', '.BAT'):
            data=p.read_text(encoding='ascii').replace('\r\n','\n').replace('\n','\r\n').encode('ascii')
            p.write_bytes(data)
            (work/p.name).write_bytes(data)
    for stem in ('C1H2D','C1D2H'):
        for ext in ('EXE','OBJ','LST','MAP'):
            (work/f'{stem}.{ext}').unlink(missing_ok=True)

    cases=[]
    def add(stem, prefix, raw, value, bad_count=0):
        count=sum(c['id'].startswith(prefix) for c in cases)
        cases.append({'id':f'{prefix}{count:04d}', 'program':stem,
                      'input':raw, 'expected':str(value), 'invalid_lines':bad_count})
    for n in range(256):
        for s in sorted(set((format(n,'X'),format(n,'x'),format(n,'02X'),format(n,'02x')))):
            add('C1H2D','H',s+'\r\n',n)
    for s in ('aF','Ff','bC','Ab','f0'):
        add('C1H2D','H',s+'\r\n',int(s,16))

    numbers=set(range(21)) | {n*257 for n in range(256)}
    for base in (10,16,100,255,256,1000,4096,10000,32768,65535):
        numbers.update(n for n in range(base-2,base+3) if 0<=n<=65535)
    for n in sorted(numbers):
        add('C1D2H','D',str(n)+'\r\n',format(n,'X'))
    for s in ('00000','00001','00010','00255','01000'):
        add('C1D2H','D',s+'\r\n',format(int(s),'X'))

    for invalid in ('','G','g','1G','/','@','[','`','{','-1','+F','0xF','100','000','F F',' FF','FF ','F'*20):
        add('C1H2D','I',invalid+'\r\nFF\r\n',255,1)
    for invalid in ('','-1','+1','1A','0x10','1 0',' 1','1 ','65536','65539','70000','99999','100000','000000','9'*20):
        add('C1D2H','J',invalid+'\r\n65535\r\n','FFFF',1)
    add('C1H2D','I','G\r\n100\r\n\r\nf\r\n',15,3)
    add('C1D2H','J','65536\r\n99999\r\n\r\n16\r\n','10',3)

    lines=['@echo off','cd \\work']
    for i,stem in enumerate(('C1H2D','C1D2H'),1):
        lines.extend([f'masm {stem}.ASM,{stem}.OBJ,{stem}.LST; > d:\\tests\\c1\\ASM{i}.LOG',
                      'if errorlevel 1 goto fail',
                      f'link {stem}.OBJ,{stem}.EXE,{stem}.MAP; > d:\\tests\\c1\\LNK{i}.LOG',
                      'if errorlevel 1 goto fail'])
    for case in cases:
        name=case['id']
        (tests/(name+'.IN')).write_bytes(case['input'].encode('ascii'))
        (tests/(name+'.OUT')).unlink(missing_ok=True)
        lines.extend([f'{case["program"]} < d:\\tests\\c1\\{name}.IN > d:\\tests\\c1\\{name}.OUT',
                      'if errorlevel 1 goto fail'])
    lines.extend(['echo C1_ALL_COMPLETE > d:\\tests\\c1\\RESULT.TXT','goto end',':fail',
                  'echo C1_FAILED > d:\\tests\\c1\\RESULT.TXT',':end'])
    (tests/'C1TEST.BAT').write_bytes(('\r\n'.join(lines)+'\r\n').encode('ascii'))
    (tests/'RESULT.TXT').unlink(missing_ok=True)
    config=course/'tmp/c1test.conf'
    config.write_bytes((course/'dosbox-course.conf').read_bytes()+b'\r\ncall d:\\tests\\c1\\c1test.bat\r\nexit\r\n')
    env=os.environ.copy()
    env.pop('SDL_VIDEODRIVER',None);env.pop('SDL_AUDIODRIVER',None)
    startup=subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow=subprocess.SW_HIDE
    process=subprocess.run([str(course/'tools/dosbox-x/dosbox-x.exe'),'-noconsole','-conf',str(config)],
                           cwd=tests,env=env,startupinfo=startup,
                           creationflags=subprocess.CREATE_NO_WINDOW,timeout=55,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (tests/'HOST.TXT').write_bytes(process.stdout+process.stderr)
    def read(name):
        p=tests/name
        return p.read_text(encoding='cp437') if p.exists() else ''

    checks={'dosbox_exit_zero':process.returncode==0,
            'batch_completed':'C1_ALL_COMPLETE' in read('RESULT.TXT')}
    for i,stem in enumerate(('C1H2D','C1D2H'),1):
        asm,link=read(f'ASM{i}.LOG'),read(f'LNK{i}.LOG')
        checks[stem+'_assembler_zero_warnings_errors']=all(
            re.search(r'0\s+'+kind+r'\s+Errors',asm) for kind in ('Warning','Severe'))
        checks[stem+'_linker_success']=bool(link.strip()) and not re.search(r'\b(error|warning)\b',link,re.I)
        p=work/(stem+'.EXE')
        checks[stem+'_dos_executable']=p.exists() and p.read_bytes()[:2]==b'MZ'
    records=[]
    for case in cases:
        output=read(case['id']+'.OUT')
        label='Dec' if case['program']=='C1H2D' else 'Hex'
        found=re.findall(r'The '+label+r' number:\s*\n([0-9A-F]+)\s*(?:\n|$)',output)
        actual=found[0] if len(found)==1 else ''
        count=output.count('Invalid input.')
        passed=actual==case['expected'] and count==case['invalid_lines']
        checks[case['id']]=passed
        records.append({**case,'actual':actual,'observed_invalid_lines':count,'pass':passed})
    summary={'verified_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
             'status':'PASS' if all(checks.values()) else 'FAIL',
             'passed':sum(bool(v) for v in checks.values()),'total':len(checks),
             'case_count':len(cases),'case_passed':sum(r['pass'] for r in records),
             'hex_to_decimal_cases':sum(c['program']=='C1H2D' for c in cases),
             'decimal_to_hex_cases':sum(c['program']=='C1D2H' for c in cases),
             'invalid_input_cases':sum(c['invalid_lines']>0 for c in cases),
             'environment':{'emulator':'DOSBox-X 2026.10.01','assembler':'MASM 5.00','linker':'Microsoft LINK 3.60'},
             'sha256':{f'{folder}/{p.name}':hashlib.sha256(p.read_bytes()).hexdigest()
                       for folder,paths in [('src',list((HERE/'src').glob('*.ASM'))),
                                            ('bin',[work/'C1H2D.EXE',work/'C1D2H.EXE'])]
                       for p in paths if p.exists()},
             'failed_checks':[k for k,v in checks.items() if not v]}
    (HERE/'验证结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if not all(checks.values()):
        for r in records:
            if not r['pass']:
                print(r,repr(read(r['id']+'.OUT')))
                break
        for n in ('ASM1.LOG','LNK1.LOG','ASM2.LOG','LNK2.LOG'):
            print(n,read(n))
        raise SystemExit(1)

    for folder in ('bin','logs','output'):
        (HERE/folder).mkdir(exist_ok=True)
    for stem in ('C1H2D','C1D2H'):
        shutil.copy2(work/(stem+'.EXE'),HERE/'bin'/(stem+'.EXE'))
        for ext in ('LST','MAP'):
            shutil.copy2(work/(stem+'.'+ext),HERE/'logs'/(stem+'.'+ext))
    for n in ('ASM1.LOG','LNK1.LOG','ASM2.LOG','LNK2.LOG'):
        shutil.copy2(tests/n,HERE/'logs'/n)
    csv_file=io.StringIO(newline='')
    fields=('id','program','input','expected','actual','invalid_lines','observed_invalid_lines','pass')
    writer=csv.DictWriter(csv_file,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for r in records:
        row=dict(r);row['input']=row['input'].replace('\r','\\r').replace('\n','\\n')
        writer.writerow(row)
    (HERE/'logs/测试记录.csv').write_text(csv_file.getvalue(),encoding='utf-8')
    examples=[('C1H2D','ff\r\n','十六进制_ff.txt'),('C1H2D','a\r\n','十六进制_a.txt'),
              ('C1D2H','255\r\n','十进制_255.txt'),('C1D2H','65535\r\n','十进制_65535.txt'),
              ('C1D2H','65536\r\n65535\r\n','越界输入后重试.txt')]
    for stem,raw,target in examples:
        case=next(c for c in cases if c['program']==stem and c['input']==raw)
        shutil.copy2(tests/(case['id']+'.OUT'),HERE/'output'/target)


if __name__=='__main__':
    main()
