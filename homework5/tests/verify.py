"""Build the DOS programs, exercise every valid input, and trace recursive CALL/RET."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess

HERE = Path(__file__).resolve().parents[1]
PROGRAMS = ('H5FIB', 'H5CFIB')


def dos_text(path, text):
    path.write_bytes(text.replace('\n', '\r\n').encode('ascii'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-root', type=Path, default=HERE.parents[1])
    course = parser.parse_args().course_root.resolve()
    work, test = course/'dos/work', course/'dos/tests/H5'
    test.mkdir(parents=True, exist_ok=True)
    (course/'tmp').mkdir(exist_ok=True)
    for p in sorted((HERE/'src').iterdir()):
        if p.suffix.upper() in ('.ASM', '.C', '.BAT'):
            dos_text(work/p.name, p.read_text(encoding='ascii'))

    def read(p):
        return p.read_text(encoding='cp437')

    def run_dos(tag, lines):
        marker = test/(tag+'.OK')
        marker.unlink(missing_ok=True)
        script = 'H5'+tag+'.BAT'
        dos_text(test/script, '\n'.join(['@echo off','cd \\work', *lines,
                 f'echo PASS > d:\\tests\\h5\\{marker.name}', 'goto end', ':fail', ':end'])+'\n')
        config = course/'tmp'/('H5'+tag+'.conf')
        config.write_bytes((course/'dosbox-course.conf').read_bytes()+
                           f'\r\ncall d:\\tests\\h5\\{script}\r\nexit\r\n'.encode('ascii'))
        env = os.environ.copy()
        env.pop('SDL_VIDEODRIVER', None)
        env.pop('SDL_AUDIODRIVER', None)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        result = subprocess.run([str(course/'tools/dosbox-x/dosbox-x.exe'), '-noconsole',
                                 '-conf', str(config)], cwd=test, env=env, startupinfo=startup,
                                creationflags=subprocess.CREATE_NO_WINDOW, timeout=50,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode or not marker.exists() or read(marker).strip()!='PASS':
            raise RuntimeError(f'DOS batch {tag} failed; see {test}')

    watcom=course/'tools/watcom'
    env={**os.environ,'WATCOM':str(watcom),'INCLUDE':str(watcom/'h'),
         'PATH':str(watcom/'binnt')+os.pathsep+os.environ.get('PATH','')}
    opts=['-0','-ms','-bt=dos','-l=dos','-od','-d2','-s','-k4096','-w=4','-we']
    cc=subprocess.run([str(watcom/'binnt/wcl.exe'),*opts,'-fe=H5CFIB.EXE','-fo=H5CFIB.OBJ',
                       '-fm=H5CFIB.MAP','H5CFIB.C'],cwd=work,env=env,check=True,timeout=40,
                      stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (test/'C.LOG').write_bytes(cc.stdout)
    subprocess.run([str(watcom/'binnt/wdis.exe'),'-s=H5CFIB.C','-l=H5CFIB.TXT','H5CFIB.OBJ'],
                   cwd=work,env=env,check=True,timeout=30)
    c_map=read(work/'H5CFIB.MAP')
    c_dis=read(work/'H5CFIB.TXT')
    c_fib=int(re.search(r'\b[0-9A-F]+:([0-9A-F]+)\+?\s+fib_',c_map,re.I)[1],16)
    c_fib_obj=int(re.search(r'^([0-9A-F]+)\s+fib_:',c_dis,re.M)[1],16)
    c_next_obj=int(re.search(r'^([0-9A-F]+)\s+read_index_:',c_dis,re.M)[1],16)
    c_fib_len=c_next_obj-c_fib_obj
    c_main=int(re.search(r'\b[0-9A-F]+:([0-9A-F]+)\+?\s+main_',c_map,re.I)[1],16)
    c_main_len=int(re.findall(r'Routine Size:\s*(\d+) bytes',c_dis)[-1])
    fib_obj_body=c_dis.split('fib_:',1)[1].split('read_index_:',1)[0]
    main_obj_body=c_dis.split('main_:',1)[1]
    def call_sites(body):
        return [int(x,16)+c_fib-c_fib_obj for x in
                re.findall(r'^([0-9A-F]+)\s+E8 [^\n]+\bcall\s+fib_',body,re.M)]
    c_right=call_sites(fib_obj_body)[1]
    c_root=call_sites(main_obj_body)[0]

    run_dos('BUILD',[
        'masm H5FIB.ASM,H5FIB.OBJ,H5FIB.LST; > d:\\tests\\h5\\ASM.LOG', 'if errorlevel 1 goto fail',
        'link H5FIB.OBJ,H5FIB.EXE,H5FIB.MAP; > d:\\tests\\h5\\LINK.LOG', 'if errorlevel 1 goto fail'])
    listing=read(work/'H5FIB.LST')
    def label(name):
        return int(re.search(r'^\s*([0-9A-F]{4})\s+(?:C\s+)?'+name+r'(?::|\s+PROC\b)',listing,re.M)[1],16)
    root, left, right, entry, ret = map(label,('ROOT_CALL','RECURSE_LEFT','RECURSE_RIGHT','FIB','FIB_RETURN'))

    def setup(n):
        # Initialize DS using the program's first two instructions, then supply AX directly.
        return ['tm 1','t','t','r ax',f'{n:x}','r ip',f'{root:x}']

    actions=[]
    ready={0,1}
    def trace(n, callsite, depth):
        actions.append(('CALL',n,depth,callsite,entry))
        if n not in ready:
            trace(n-1,left,depth+1)
            trace(n-2,right,depth+1)
            ready.add(n)
        actions.append(('RET',n,depth,ret,callsite+3))

    trace(5,root,1)
    lines=setup(5)
    for i,(_,_,_,site,_) in enumerate(actions):
        if i: lines.append(f'g {site:x}')
        lines.extend(['r','t'])
    lines.extend(['g','q'])
    dos_text(test/'TRACE5.IN','\n'.join(lines)+'\n')
    saved=entry+4  # Four one-byte PUSH instructions at the procedure entry.
    dos_text(test/'MAX100.IN','\n'.join(setup(100)+['r','t',f'g {right:x}','r','t',f'g {saved:x}','r','t',
                                                    f'g {ret:x}','r','t','g','q'])+'\n')
    dos_text(test/'CDIS.IN',f'r\nu cs:{c_fib:x} l{c_fib_len:x}\nu cs:{c_main:x} l{c_main_len:x}\nq\n')
    # Stop after main's prologue, bypass the I/O, and measure the first F(0) frame.
    c_frame=c_fib+12
    dos_text(test/'CMAX100.IN','\n'.join([f'g {c_main+12:x}','r ax','64','r ip',f'{c_root:x}',
               'r','t',f'g {c_right:x}','r','t',f'g {c_frame:x}','r','t',f'g {c_root+3:x}',
               'r','t','g','q'])+'\n')

    fib=[0,1]
    for _ in range(2,101):
        fib.append(fib[-1]+fib[-2])
    cases=[(f'N{n:03d}',f'{n}\n',n,0) for n in range(1,101)]
    cases.extend((f'B{i:03d}',s, n, count) for i,(s,n,count) in enumerate([
        ('001\n',1,0),('099\n',99,0),('\n5\n',5,1),('0\n5\n',5,1),('101\n5\n',5,1),
        ('-1\n5\n',5,1),('a\n5\n',5,1),('1000\n5\n',5,1),(' 5\n5\n',5,1),
        ('5 \n5\n',5,1),('0\n101\n-1\n100\n',100,3)]))
    batch=[]
    for case,stdin,_,_ in cases:
        dos_text(test/(case+'.IN'),stdin)
        for prefix,stem in zip('AC',PROGRAMS):
            batch.extend([f'{stem} < d:\\tests\\h5\\{case}.IN > d:\\tests\\h5\\{prefix}{case}.OUT',
                          'if errorlevel 1 goto fail'])
    for name,stem in (('TRACE5','H5FIB'),('MAX100','H5FIB'),('CDIS','H5CFIB'),('CMAX100','H5CFIB')):
        batch.append(f'debug {stem}.EXE < d:\\tests\\h5\\{name}.IN > d:\\tests\\h5\\{name}.DBG')
    run_dos('RUN',batch)

    checks={}
    for stem in PROGRAMS:
        exe=(work/(stem+'.EXE')).read_bytes()
        checks[stem+'_mz']=exe[:2]==b'MZ'
    checks['masm_no_diagnostics']=all(re.search(r'0\s+'+kind, read(test/'ASM.LOG'))
                                     for kind in ('Warning Errors','Severe\s+Errors'))
    checks['link_no_diagnostics']=not re.search(r'\b(?:error|warning)\b',read(test/'LINK.LOG'),re.I)
    checks['watcom_8086_clean']=b'0 warnings, 0 errors' in cc.stdout and 'USE16' in c_dis
    rows=[]
    for case,_,n,invalid in cases:
        for prefix,stem in zip('AC',PROGRAMS):
            out=read(test/(prefix+case+'.OUT'))
            values=re.findall(r'^Fibonacci number:\n([0-9]+)\n',out,re.M)
            found=values[0] if len(values)==1 else ''
            ok=found==str(fib[n]) and out.count('Invalid input.')==invalid
            checks[prefix+case]=ok
            rows.append((stem,case,n,str(fib[n]),found,invalid,ok))

    def registers(block):
        regs=re.search(r'^(AX=.*)\n(DS=.*)$',block,re.M)
        if not regs:
            raise RuntimeError('No register dump in '+block[:200])
        return {key:int(value,16) for key,value in re.findall(r'([A-Z]{2})=([0-9A-F]{4})',' '.join(regs.groups()))}

    trace_log=read(test/'TRACE5.DBG')
    pairs=re.findall(r'^-r\n(.*?)^-t\n(.*?)(?=^-|\Z)',trace_log,re.M|re.S)
    checks['all_trace_events_present']=len(pairs)==len(actions)
    events=[]
    for i,((kind,n,depth,site,dest),(before,after)) in enumerate(zip(actions,pairs),1):
        b,a=registers(before),registers(after)
        correct=(b['IP']==site and a['IP']==dest and a['SP']-b['SP']==(-2 if kind=='CALL' else 2))
        if kind=='CALL': correct=correct and b['AX']==n
        checks[f'trace_{i}']=correct
        events.append((i,kind,n,depth,f'{b["IP"]:04X}',f'{a["IP"]:04X}',f'{b["SP"]:04X}',f'{a["SP"]:04X}'))

    max_log=read(test/'MAX100.DBG')
    max_pairs=re.findall(r'^-r\n(.*?)^-t\n(.*?)(?=^-|\Z)',max_log,re.M|re.S)
    starts=[registers(b) for b,_ in max_pairs]
    sp_initial=starts[0]['SP']
    sp_low=starts[2]['SP']
    measured=sp_initial-sp_low
    checks['stack_100_reaches_f0_right_call']=len(starts)==4 and starts[1]['AX']==0 and starts[1]['IP']==right
    checks['stack_100_low_water_matches_bound']=starts[2]['IP']==saved and starts[-1]['IP']==ret and measured==1002
    checks['debug_5_finishes']='\n5\n' in trace_log and 'Program terminated normally (0000)' in trace_log
    checks['debug_100_finishes']=f'\n{fib[100]}\n' in max_log and 'Program terminated normally (0000)' in max_log
    c_max_log=read(test/'CMAX100.DBG')
    c_starts=[registers(b) for b in re.findall(r'^-r\n(.*?)^-t\n',c_max_log,re.M|re.S)]
    c_sp_initial,c_sp_low=c_starts[0]['SP'],c_starts[2]['SP']
    c_measured=c_sp_initial-c_sp_low
    checks['c_stack_100_bound_and_restoration']=(len(c_starts)==4 and c_starts[1]['AX']==0 and
        c_starts[1]['IP']==c_right and c_starts[2]['IP']==c_frame and c_measured==3400 and
        c_starts[3]['IP']==c_root+3 and c_starts[3]['SP']==c_sp_initial)
    checks['debug_c_100_finishes']=f'\n{fib[100]}\n' in c_max_log and 'Program terminated normally (0000)' in c_max_log
    c_log=read(test/'CDIS.DBG')
    blocks=re.findall(r'^-u [^\n]+\n(.*?)(?=^-|\Z)',c_log,re.M|re.S)
    c_bytes=[sum(len(x)//2 for x in re.findall(r'^\w{4}:\w{4}\s+([0-9A-F]+)\s+',block,re.M)) for block in blocks]
    checks['c_disassembly_complete']=c_bytes==[c_fib_len,c_main_len]
    checks['c_has_two_real_recursive_calls']=len(blocks)>=1 and len(re.findall(r'\bCALL\s+'+f'{c_fib:04X}'+r'\b',blocks[0]))==2
    checks['debug_no_command_errors']=not re.search(r'\^\s*error\b|syntax error|file not found',trace_log+max_log+c_log+c_max_log,re.I)

    failed=[k for k,v in checks.items() if not v]
    if failed:
        raise RuntimeError(f'Failed {failed}; see raw results in {test}')
    for folder in ('bin','logs','output'):
        (HERE/folder).mkdir(exist_ok=True)
    for stem in PROGRAMS:
        shutil.copy2(work/(stem+'.EXE'),HERE/'bin'/(stem+'.EXE'))
    for p in [work/'H5FIB.LST', work/'H5FIB.MAP', work/'H5CFIB.MAP', work/'H5CFIB.TXT',
              *(test/name for name in ('ASM.LOG','LINK.LOG','C.LOG','TRACE5.IN','TRACE5.DBG',
                                       'MAX100.IN','MAX100.DBG','CDIS.IN','CDIS.DBG','CMAX100.IN','CMAX100.DBG'))]:
        shutil.copy2(p,HERE/'logs'/p.name)
    for case in ('N001','N005','N047','N094','N100','B010'):
        for prefix in 'AC':
            shutil.copy2(test/(prefix+case+'.OUT'),HERE/'output'/(prefix+case+'.txt'))

    def write_csv(path,header,entries):
        buf=io.StringIO(newline='')
        writer=csv.writer(buf,lineterminator='\n')
        writer.writerow(header)
        writer.writerows(entries)
        path.write_text(buf.getvalue(),encoding='utf-8')

    write_csv(HERE/'logs/输入测试.csv',('program','case','n','expected','actual','invalid_lines','pass'),rows)
    write_csv(HERE/'logs/递归跟踪.csv',('step','instruction','n','depth','ip_before','ip_after','sp_before','sp_after'),events)
    summary={'status':'PASS','passed':len(checks),'total':len(checks),'input_cases':len(rows),
             'trace_events':len(events),'f100':str(fib[100]),'stack_high_water_asm_bytes':measured,
             'stack_asm_declared_bytes':4096,'stack_c_header_sp':struct.unpack_from('<H',(work/'H5CFIB.EXE').read_bytes(),16)[0],
             'stack_high_water_c_fib_bytes':c_measured,'stack_c_sp_before_call':f'{c_sp_initial:04X}',
             'stack_c_min_observed_sp':f'{c_sp_low:04X}',
             'trace_offsets':{key:f'{value:04X}' for key,value in zip(('root','left','right','entry','ret'),(root,left,right,entry,ret))},
             'c_fib':{'offset':f'{c_fib:04X}','bytes':c_fib_len},'c_main':{'offset':f'{c_main:04X}','bytes':c_main_len},
             'sha256':{f'{p.parent.name}/{p.name}':hashlib.sha256((work/p.name).read_bytes()).hexdigest()
                       for folder in ('src','bin') for p in sorted((HERE/folder).iterdir()) if p.is_file()}}
    (HERE/'验证结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
