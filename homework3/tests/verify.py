"""Build and exercise the 16-bit programs in the shared DOSBox-X environment."""
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
STEMS = ('S3REG', 'S3DATA', 'S3STACK', 'S3INPUT')


def dos_text(path, text):
    path.write_bytes(text.replace('\r\n', '\n').replace('\n', '\r\n').encode('ascii'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--course-root', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    course = args.course_root.resolve()
    work, tests = course/'dos/work', course/'dos/tests/H3'
    tests.mkdir(parents=True, exist_ok=True)
    for p in (HERE/'src').iterdir():
        if p.suffix.upper() in ('.ASM', '.INC', '.C', '.BAT'):
            dos_text(p, p.read_text(encoding='ascii'))
            shutil.copy2(p, work/p.name)
    for stem in STEMS + ('S3C',):
        for ext in ('EXE', 'OBJ', 'LST', 'MAP'):
            (work/f'{stem}.{ext}').unlink(missing_ok=True)

    def read(name):
        p = tests/name
        return p.read_text(encoding='cp437') if p.exists() else ''

    def launch(batch, tag):
        config = course/f'tmp/h3{tag}.conf'
        config.write_bytes((course/'dosbox-course.conf').read_bytes()
                           + f'\r\ncall d:\\tests\\h3\\{batch}\r\nexit\r\n'.encode('ascii'))
        env = os.environ.copy()
        env.pop('SDL_VIDEODRIVER', None)
        env.pop('SDL_AUDIODRIVER', None)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        result = subprocess.run(
            [str(course/'tools/dosbox-x/dosbox-x.exe'), '-noconsole', '-conf', str(config)],
            cwd=tests, env=env, startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=55, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (tests/f'HOST{tag}.TXT').write_bytes(result.stdout+result.stderr)
        return result.returncode

    env = os.environ.copy()
    env['WATCOM'] = str(course/'tools/watcom')
    env['INCLUDE'] = str(course/'tools/watcom/h')
    env['PATH'] = str(course/'tools/watcom/binnt') + os.pathsep + env.get('PATH', '')
    options = ['-0', '-ms', '-bt=dos', '-l=dos', '-od', '-d2', '-s', '-w=4', '-we']
    compile_c = subprocess.run(
        [str(course/'tools/watcom/binnt/wcl.exe')]+options+
        ['-fe=S3C.EXE','-fo=S3C.OBJ','-fm=S3C.MAP','S3C.C'],
        cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
    (tests/'CCOMP.LOG').write_bytes(compile_c.stdout)
    if compile_c.returncode:
        raise RuntimeError(compile_c.stdout.decode('cp437'))
    dis = subprocess.run([str(course/'tools/watcom/binnt/wdis.exe'),'-s=S3C.C',
                          '-l=S3C_DIS.TXT','S3C.OBJ'],cwd=work,env=env,
                         stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    if dis.returncode:
        raise RuntimeError(dis.stdout.decode('cp437'))
    c_listing = (work/'S3C_DIS.TXT').read_text(encoding='cp437')
    routine_size = int(re.search(r'Routine Size:\s*(\d+) bytes', c_listing)[1])
    c_map = (work/'S3C.MAP').read_text(encoding='cp437')
    c_main = int(re.search(r'[0-9A-Fa-f]+:([0-9A-Fa-f]+)\s+main_', c_map)[1],16)

    cases = []
    for n in range(1,101):
        cases.append({'id':f'N{n:03d}', 'input':str(n)+'\r\n',
                      'n':n, 'invalid_lines':0})
    for i,s in enumerate(('01','001','010','099')):
        cases.append({'id':f'L{i:03d}', 'input':s+'\r\n',
                      'n':int(s),'invalid_lines':0})
    invalid = ('','0','00','000','101','999','-1','+1','1A','1.5','1000',
               '65535','0x10','1 0',' 1','1 ','a'*20)
    for i,s in enumerate(invalid):
        cases.append({'id':f'B{i:03d}', 'input':s+'\r\n100\r\n',
                      'n':100, 'invalid_lines':1})
    cases.append({'id':'RETRY','input':'0\r\n101\r\nx\r\n10\r\n',
                  'n':10,'invalid_lines':3})
    lines = ['@echo off','cd \\work']
    for stem in STEMS:
        lines.extend([f'masm {stem}.ASM,{stem}.OBJ,{stem}.LST; > d:\\tests\\h3\\{stem}.LOG',
                      'if errorlevel 1 goto fail',
                      f'link {stem}.OBJ,{stem}.EXE,{stem}.MAP; > d:\\tests\\h3\\L{stem[2:]}.LOG',
                      'if errorlevel 1 goto fail'])
    fixed = ('S3REG','S3DATA','S3STACK','S3C')
    for stem in fixed:
        (tests/(stem+'.OUT')).unlink(missing_ok=True)
        lines.extend([f'{stem} > d:\\tests\\h3\\{stem}.OUT','if errorlevel 1 goto fail'])
    for case in cases:
        name = case['id']
        dos_text(tests/(name+'.IN'),case['input'])
        (tests/(name+'.OUT')).unlink(missing_ok=True)
        lines.extend([f'S3INPUT < d:\\tests\\h3\\{name}.IN > d:\\tests\\h3\\{name}.OUT',
                      'if errorlevel 1 goto fail'])
    lines.extend(['echo H3_RUN_COMPLETE > d:\\tests\\h3\\RESULT.TXT', 'goto end',
                  ':fail','echo H3_FAILED > d:\\tests\\h3\\RESULT.TXT',':end'])
    dos_text(tests/'H3TEST.BAT','\n'.join(lines)+'\n')
    (tests/'RESULT.TXT').unlink(missing_ok=True)
    code = launch('H3TEST.BAT','run')
    if code or 'H3_RUN_COMPLETE' not in read('RESULT.TXT'):
        for n in ('S3REG.LOG','LREG.LOG','S3DATA.LOG','LDATA.LOG',
                  'S3STACK.LOG','LSTACK.LOG','S3INPUT.LOG','LINPUT.LOG'):
            print(n,read(n))
        raise RuntimeError('DOS assembly or execution failed')

    def public(stem, symbol):
        mapping = (work/(stem+'.MAP')).read_text(encoding='cp437')
        match = re.search(r'([0-9A-Fa-f]+):([0-9A-Fa-f]+)\s+'+symbol+r'\b',mapping)
        if match:
            return int(match[2],16)
        # LINK 3.60's basic map has segments only; use the MASM listing.
        listing=(work/(stem+'.LST')).read_text(encoding='cp437')
        label=re.search(r'^\s*([0-9A-F]{4})\s+'+symbol+r':',listing,re.M)
        if label:
            return int(label[1],16)
        word=re.search(r'^\s*([0-9A-F]{4})\s+[0-9A-F]{4}\s+'+symbol+r'\s+DW',listing,re.M)
        data=re.search(r'^\s*([0-9A-F]+)H\s+[^\n]+\b_DATA\s+DATA',mapping,re.M)
        group=re.search(r'^\s*([0-9A-F]+):0\s+DGROUP',mapping,re.M)
        if word and data and group:
            return int(word[1],16)+int(data[1],16)-16*int(group[1],16)
        raise RuntimeError(f'Missing symbol {symbol} in {stem} map/listing')

    done = {s:public(s,'SUM_DONE') for s in STEMS[:3]}
    result_offset = public('S3DATA','RESULT')
    cleanup = public('S3STACK','STACK_DONE')
    scripts = {
        'REG': f'tm 1\nu cs:0 l{done["S3REG"]:x}\ng=0 {done["S3REG"]:x}\nr\ng\nq\n',
        'DATA': f'tm 1\nu cs:0 l{done["S3DATA"]:x}\ng=0 {done["S3DATA"]:x}\nr\nd ds:{result_offset:x} l2\nt\nr\ng\nq\n',
        'STACK': f'tm 1\nu cs:0 l{done["S3STACK"]:x}\ng=0 {done["S3STACK"]:x}\nr\nd ss:sp l2\nt\nr\ng {cleanup:x}\nr\ng\nq\n',
        'C':f'r\nu cs:{c_main:x} l{routine_size:x}\ng {c_main:x}\nr\ng\nq\n',
    }
    debug_batch=['@echo off','cd \\work']
    for key,script in scripts.items():
        dos_text(tests/(key+'.IN'),script)
        (tests/(key+'.DBG')).unlink(missing_ok=True)
        stem='S3C' if key=='C' else 'S3'+key
        debug_batch.append(f'debug {stem}.EXE < d:\\tests\\h3\\{key}.IN > d:\\tests\\h3\\{key}.DBG')
    debug_batch.append('echo H3_DEBUG_COMPLETE > d:\\tests\\h3\\DBGEND.TXT')
    dos_text(tests/'H3DEBUG.BAT','\n'.join(debug_batch)+'\n')
    (tests/'DBGEND.TXT').unlink(missing_ok=True)
    debug_code = launch('H3DEBUG.BAT','dbg')

    checks = {'dosbox_run_exit_zero':code==0,'run_batch_completed':'H3_RUN_COMPLETE' in read('RESULT.TXT'),
              'c_compiler_zero_errors_warnings':b'0 warnings, 0 errors' in compile_c.stdout,
              'c_object_is_16bit':'Segment: _TEXT BYTE USE16' in c_listing,
              'dosbox_debug_exit_zero':debug_code==0,
              'debug_batch_completed':'H3_DEBUG_COMPLETE' in read('DBGEND.TXT')}
    for stem in STEMS:
        checks[stem+'_assembly_zero_errors_warnings'] = all(
            re.search(r'0\s+'+kind+r'\s+Errors',read(stem+'.LOG')) for kind in ('Warning','Severe'))
        log=read('L'+stem[2:]+'.LOG')
        checks[stem+'_link_success'] = bool(log.strip()) and not re.search(r'\b(error|warning)\b',log,re.I)
    for stem in fixed:
        checks[stem+'_output_exact_5050']=(tests/(stem+'.OUT')).read_bytes()==b'5050\r\n'
    for stem in STEMS+('S3C',):
        checks[stem+'_mz_executable']=(work/(stem+'.EXE')).read_bytes()[:2]==b'MZ'
    records=[]
    for case in cases:
        output=read(case['id']+'.OUT')
        found=re.findall(r'The sum:\s*\n([0-9]+)\s*(?:\n|$)',output)
        actual=found[0] if len(found)==1 else ''
        expected=str(case['n']*(case['n']+1)//2)
        bad_count=output.count('Invalid input.')
        passed=actual==expected and bad_count==case['invalid_lines']
        checks[case['id']]=passed
        records.append({**case,'expected':expected,'actual':actual,
                        'observed_invalid_lines':bad_count,'pass':passed})
    reg,data,stack,c=(read(k+'.DBG') for k in ('REG','DATA','STACK','C'))
    checks['register_sum_in_ax'] = 'AX=13BA' in reg and 'CX=0000' in reg and 'BX=0065' in reg
    checks['data_sum_in_memory'] = 'BA 13' in data and 'AX=13BA' in data
    checks['stack_sum_in_memory'] = 'BA 13' in stack and 'AX=13BA' in stack and 'BP=00FE' in stack
    checks['stack_frame_restored'] = bool(re.search(r'SP=0100 BP=0000',stack))
    checks['c_main_breakpoint_reached'] = f'IP={c_main:04X}' in c
    for key,log in (('REG',reg),('DATA',data),('STACK',stack),('C',c)):
        checks[key+'_debug_normal_output_exit']='5050' in log and 'Program terminated normally (0000)' in log
    all_debug='\n'.join((reg,data,stack,c)).lower()
    checks['debug_no_command_errors'] = not any(s in all_debug for s in
                                               ('syntax error','file not found','invalid opcode','error in')) and not re.search(r'\^\s*error\b',all_debug)
    summary={'verified_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
             'status':'PASS' if all(checks.values()) else 'FAIL','passed':sum(bool(v) for v in checks.values()),
             'total':len(checks),'input_case_count':len(cases),'input_case_passed':sum(r['pass'] for r in records),
             'full_range_n':'1..100','invalid_input_cases':sum(c['invalid_lines']>0 for c in cases),
             'fixed_program_count':len(fixed),'fixed_output':'5050\r\n',
             'c_main_offset':f'{c_main:04X}','c_main_bytes':routine_size,
             'debug_offsets':{**{s:f'{v:04X}' for s,v in done.items()},'RESULT':f'{result_offset:04X}',
                              'STACK_DONE':f'{cleanup:04X}'},
             'environment':{'assembler':'MASM 5.00','linker':'Microsoft LINK 3.60',
                            'emulator':'DOSBox-X 2026.10.01','C_compiler':'Open Watcom C16 2.0beta1 LA'},
             'sha256':{f'{folder}/{p.name}':hashlib.sha256(p.read_bytes()).hexdigest()
                       for folder,paths in [('src',list((HERE/'src').glob('*.ASM'))+
                                             list((HERE/'src').glob('*.INC'))+list((HERE/'src').glob('*.C'))),
                                            ('bin',[work/(s+'.EXE') for s in STEMS+('S3C',)])]
                       for p in paths},
             'failed_checks':[k for k,v in checks.items() if not v]}
    (HERE/'验证结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if not all(checks.values()):
        for record in records:
            if not record['pass']:
                print(record,repr(read(record['id']+'.OUT')))
                break
        raise RuntimeError('Verification failed')
    for folder in ('bin','logs','output'):
        (HERE/folder).mkdir(exist_ok=True)
    for stem in STEMS+('S3C',):
        shutil.copy2(work/(stem+'.EXE'),HERE/'bin'/(stem+'.EXE'))
        for ext in ('LST','MAP'):
            p=work/(stem+'.'+ext)
            if p.exists(): shutil.copy2(p,HERE/'logs'/p.name)
    shutil.copy2(work/'S3C_DIS.TXT',HERE/'logs/S3C_DIS.TXT')
    for p in tests.iterdir():
        if p.suffix in ('.LOG','.DBG') or p.name in ('REG.IN','DATA.IN','STACK.IN','C.IN'):
            shutil.copy2(p,HERE/'logs'/p.name)
    for stem in fixed:
        shutil.copy2(tests/(stem+'.OUT'),HERE/'output'/(stem+'.txt'))
    for name in ('N001','N010','N100','B004','RETRY'):
        shutil.copy2(tests/(name+'.OUT'),HERE/'output'/(name+'.txt'))
    csv_text=io.StringIO(newline='')
    fields=('id','input','n','expected','actual','invalid_lines','observed_invalid_lines','pass')
    writer=csv.DictWriter(csv_text,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for record in records:
        row=dict(record);row['input']=row['input'].replace('\r','\\r').replace('\n','\\n')
        writer.writerow(row)
    (HERE/'logs/输入测试记录.csv').write_text(csv_text.getvalue(),encoding='utf-8')


if __name__=='__main__':
    main()
