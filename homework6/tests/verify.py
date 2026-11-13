"""Build 8086 DOS programs, check 2400 months, and trace segmented calls."""
import argparse
import calendar
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parents[1]


def dos_text(path, text):
    path.write_bytes(text.replace('\r\n', '\n').replace('\n', '\r\n').encode('ascii'))


def expected(year, month):
    # Independent standard-library Gregorian implementation, Sunday first.
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
    lines = [f'{year}  {calendar.month_name[month]}', 'Su Mo Tu We Th Fr Sa']
    for week in weeks:
        lines.append(' '.join(f'{day:2d}' if day else '  ' for day in week).rstrip())
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-root', type=Path, default=HERE.parents[1])
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    course = args.course_root.resolve()
    work, scratch = course/'dos/work', course/'dos/tests/H6'
    scratch.mkdir(parents=True, exist_ok=True)
    for folder in ('bin', 'logs', 'output'):
        (HERE/folder).mkdir(exist_ok=True)
    for p in (HERE/'src').iterdir():
        dos_text(work/p.name, p.read_text(encoding='ascii'))
    dos_text(work/'H6RANGE.ASM', (HERE/'tests/fixtures/H6RANGE.ASM').read_text(encoding='ascii'))

    def read(path):
        return path.read_text(encoding='cp437')

    def launch(tag, lines, timeout=60):
        marker = scratch/(tag+'.OK')
        marker.unlink(missing_ok=True)
        script = 'H6'+tag+'.BAT'
        dos_text(scratch/script, '\n'.join(['@echo off', 'cd \\work', *lines,
            f'echo PASS > d:\\tests\\h6\\{marker.name}', 'goto end', ':fail', ':end'])+'\n')
        config = course/'tmp'/('H6'+tag+'.conf')
        config.write_bytes((course/'dosbox-course.conf').read_bytes() +
            f'\r\ncall d:\\tests\\h6\\{script}\r\nexit\r\n'.encode('ascii'))
        env = os.environ.copy()
        env.pop('SDL_VIDEODRIVER', None)
        env.pop('SDL_AUDIODRIVER', None)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        proc = subprocess.run([str(course/'tools/dosbox-x/dosbox-x.exe'), '-noconsole',
            '-conf', str(config)], cwd=scratch, env=env, startupinfo=startup,
            creationflags=subprocess.CREATE_NO_WINDOW, timeout=timeout,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if proc.returncode or not marker.exists() or read(marker).strip() != 'PASS':
            raise RuntimeError(f'DOS {tag} failed; inspect {scratch}')

    checks = {}
    lines = []
    for stem in ('H6CAL', 'H6JUMP'):
        lines += [f'masm {stem}.ASM,{stem}.OBJ,{stem}.LST; > d:\\tests\\h6\\{stem}.LOG',
            'if errorlevel 1 goto fail',
            f'link {stem}.OBJ,{stem}.EXE,{stem}.MAP; > d:\\tests\\h6\\L{stem[2:]}.LOG',
            'if errorlevel 1 goto fail']
    lines += ['masm H6RANGE.ASM,H6RANGE.OBJ,H6RANGE.LST; > d:\\tests\\h6\\RANGE.LOG',
              'if not errorlevel 1 goto fail']
    launch('BUILD', lines)
    for stem in ('H6CAL', 'H6JUMP'):
        log = read(scratch/(stem+'.LOG'))
        checks[stem+'_assembly'] = all(re.search(r'0\s+'+s, log) for s in ('Warning Errors', r'Severe\s+Errors'))
        checks[stem+'_link'] = not re.search(r'\b(error|warning)\b', read(scratch/('L'+stem[2:]+'.LOG')), re.I)
    checks['short_branch_range_rejected'] = 'out of range' in read(scratch/'RANGE.LOG').lower()
    watcom = course/'tools/watcom'
    env = {**os.environ, 'WATCOM': str(watcom), 'INCLUDE': str(watcom/'h'),
           'PATH': str(watcom/'binnt')+os.pathsep+os.environ.get('PATH','')}
    cc = subprocess.run([str(watcom/'binnt/wcl.exe'), '-0','-ms','-bt=dos','-l=dos',
        '-od','-d2','-s','-k2048','-w=4','-we','-fe=H6CCAL.EXE','-fo=H6CCAL.OBJ',
        '-fm=H6CCAL.MAP','H6CAL.C'], cwd=work, env=env, timeout=40,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    (scratch/'C.LOG').write_bytes(cc.stdout)
    subprocess.run([str(watcom/'binnt/wdis.exe'),'-s=H6CAL.C','-l=H6CCAL.TXT','H6CCAL.OBJ'],
                   cwd=work, env=env, check=True, timeout=30, stdout=subprocess.PIPE)
    checks['c_build'] = b'0 warnings, 0 errors' in cc.stdout
    print('Build finished; expected short-branch diagnostic recorded.', flush=True)
    if args.build_only:
        print(checks, flush=True)
        return

    cases = [(f'M{(y-1900)*12+m:04d}', f'{y}\n{m}\n', y, m, 0)
             for y in range(1900,2100) for m in range(1,13)]
    invalid = [
        ('\n2026\n11\n',2026,11,1), ('1899\n1900\n2\n',1900,2,1),
        ('2100\n2099\n12\n',2099,12,1), ('-1\n2000\n2\n',2000,2,1),
        ('20a6\n2026\n11\n',2026,11,1), ('02026\n2026\n11\n',2026,11,1),
        (' 2026\n2026\n11\n',2026,11,1), ('2026 \n2026\n11\n',2026,11,1),
        ('2026\n\n11\n',2026,11,1), ('2026\n0\n11\n',2026,11,1),
        ('2026\n13\n11\n',2026,11,1), ('2026\n-1\n11\n',2026,11,1),
        ('2026\na\n11\n',2026,11,1), ('2026\n001\n1\n',2026,1,1),
        ('2026\n 1\n1\n',2026,1,1), ('2026\n1 \n1\n',2026,1,1),
        ('2026\n01\n',2026,1,0), ('0\n2100\n2000\n0\n13\n2\n',2000,2,4),
        ('9999999999\n2026\n99\n11\n',2026,11,2),
    ]
    cases += [(f'B{i:03d}', *c) for i,c in enumerate(invalid)]
    rows = []
    for start in range(0,len(cases),200):
        batch = []
        part = cases[start:start+200]
        for name, stdin, year, month, errors in part:
            dos_text(scratch/(name+'.IN'), stdin)
            for prefix, stem in (('A','H6CAL'),('C','H6CCAL')):
                batch += [f'{stem} < d:\\tests\\h6\\{name}.IN > d:\\tests\\h6\\{prefix}{name}.OUT',
                          'if errorlevel 1 goto fail']
        launch(f'R{start//200:02d}', batch)
        for name, _, year, month, errors in part:
            for prefix, stem in (('A','H6CAL'),('C','H6CCAL')):
                out = read(scratch/(prefix+name+'.OUT'))
                match = re.search(r'^\d{4}  [A-Z][a-z]+\nSu Mo Tu We Th Fr Sa\n', out, re.M)
                body = out[match.start():] if match else ''
                ok = body == expected(year, month) and out.count('Invalid input.') == errors
                checks[prefix+name] = ok
                rows.append((stem,name,year,month,errors,ok))
                if not ok:
                    raise RuntimeError(f'{prefix+name}: calendar/output mismatch: {out!r}')
        print(f'Calendar and input cases: {min(start+200,len(cases))}/{len(cases)} per program', flush=True)

    listing = read(work/'H6CAL.LST')
    jump_listing = read(work/'H6JUMP.LST')
    def label(name, text=listing):
        return int(re.search(r'^\s*([0-9A-F]{4})\s+(?:[0-9A-F ]+\s+)?'+name+r'(?::|\s+PROC\b)',text,re.M)[1],16)
    data_call, stack_call = label('DATA_CALL'), label('STACK_CALL')
    trace = ['tm 1','t','t','e ds:0 ea 07 0b 00','r bx','1234','r cx','5678',
             'r si','1357','r di','2468','r bp','369c','r ip',f'{data_call:x}','r','t',
             f'g {label("MONTH_DAYS"):x}','r',f'g {label("GET_DAYS_RET"):x}','r','t',
             'd ds:0 l8','t','t','t','t','r','t','t','t','d ss:bp la',
             f'g {label("FIRST_DAY_RET"):x}','r','t','r','g','q']
    dos_text(scratch/'FAR.IN','\n'.join(trace)+'\n')
    # U at each far entry follows CS automatically; disassemble the near-call site too.
    dis = ['tm 1','u cs:0 l'+f'{label("READ_NUM"):x}','t','t','e ds:0 ea 07 0b 00',
           'r ip',f'{data_call:x}','t',f'u cs:0 l{label("IS_LEAP"):x}',
           f'u cs:{label("IS_LEAP"):x} l3c','q']
    dos_text(scratch/'ADIS.IN','\n'.join(dis)+'\n')
    jsite, jfar = label('NEAR_JUMP',jump_listing), label('DISTANT',jump_listing)
    dos_text(scratch/'JUMP.IN','\n'.join(['tm 1','u cs:0 l10',f'g {jsite:x}','r','t',
        'r','u cs:ip l5','t','r','u cs:ip l11','g','q'])+'\n')
    cdis, cmap = read(work/'H6CCAL.TXT'), read(work/'H6CCAL.MAP')
    funcs = ['is_leap','month_days','first_day','read_number','print_calendar','main']
    sizes = [int(s) for s in re.findall(r'Routine Size:\s*(\d+) bytes', cdis)]
    csymbols = {f:int(re.search(r'\b[0-9A-F]+:([0-9A-F]+)\+?\s+'+f+'_',cmap,re.I)[1],16) for f in funcs}
    dos_text(scratch/'CDIS.IN','\n'.join(['r']+[f'u cs:{csymbols[f]:x} l{size:x}' for f,size in zip(funcs,sizes)]+['q'])+'\n')
    commands=[]
    for name,stem in (('FAR','H6CAL'),('ADIS','H6CAL'),('JUMP','H6JUMP'),('CDIS','H6CCAL')):
        commands.append(f'debug {stem}.EXE < d:\\tests\\h6\\{name}.IN > d:\\tests\\h6\\{name}.DBG')
    commands += ['H6JUMP > d:\\tests\\h6\\JUMP.OUT','if errorlevel 1 goto fail']
    launch('TRACE',commands)
    trace_log = read(scratch/'FAR.DBG')
    def registers(text):
        return {k:int(v,16) for k,v in re.findall(r'([A-Z]{2})=([0-9A-F]{4})',text)}
    snapshots = [registers(block) for block in re.findall(r'^-r\n(.*?)(?=^-|\Z)',trace_log,re.M|re.S)]
    checks['far_trace_snapshots'] = len(snapshots)==6
    if len(snapshots)==6:
        before, regargs, dataret, stackbefore, stackret, after = snapshots
        checks['far_changes_cs'] = before['CS']!=dataret['CS'] and before['CS']==after['CS']
        checks['register_arguments'] = regargs['AX']==2026 and regargs['BX']==11
        checks['data_call_stack'] = before['SP']==0x200 and dataret['SP']==0x1fc
        checks['stack_arguments_and_return'] = stackbefore['SP']==0x1fc and stackret['SP']==0x1f8 and after['SP']==0x200 and after['AX']==0
        checks['preserved_registers'] = all(after[r]==before[r] for r in ('BX','CX','DX','SI','DI','BP','DS'))
    checks['far_finishes'] = expected(2026,11) in trace_log and 'Program terminated normally (0000)' in trace_log
    checks['far_return_opcodes'] = 'CA0400' in read(scratch/'ADIS.DBG') and re.search(r'\bCB\s+RETF',read(scratch/'ADIS.DBG')) is not None
    jlog = read(scratch/'JUMP.DBG')
    checks['jump_demo_output'] = read(scratch/'JUMP.OUT')=='Jump OK\n'
    checks['near_far_jump_opcodes'] = re.search(r'\bE9[0-9A-F]{4}\s+JMP',jlog) is not None and re.search(r'\bEA[0-9A-F]{8}\s+JMP',jlog) is not None
    checks['debug_no_errors'] = all(not re.search(r'\^\s*error|file not found|syntax error',read(scratch/(name+'.DBG')),re.I) for name in ('FAR','ADIS','JUMP','CDIS'))
    checks['c_disassembly_functions'] = len(sizes)==6 and len(re.findall(r'^-u ',read(scratch/'CDIS.DBG'),re.M))==6
    for stem in ('H6CAL','H6CCAL','H6JUMP'):
        shutil.copy2(work/(stem+'.EXE'), HERE/'bin'/(stem+'.EXE'))
    for p in [*(scratch.glob('*.LOG')), *(scratch.glob('*.DBG')),
              *(scratch/(n+'.IN') for n in ('FAR','ADIS','JUMP','CDIS')),
              *(work/(n+ext) for n in ('H6CAL','H6JUMP') for ext in ('.MAP','.LST')),
              work/'H6RANGE.LST', work/'H6CCAL.MAP',work/'H6CCAL.TXT']:
        shutil.copy2(p,HERE/'logs'/p.name)
    selected=[(1900,1),(1900,2),(2000,2),(2026,11),(2099,12)]
    for y,m in selected:
        name=f'M{(y-1900)*12+m:04d}'
        for prefix in 'AC':
            shutil.copy2(scratch/(prefix+name+'.OUT'), HERE/'output'/f'{prefix}_{y}_{m:02d}.txt')
    for prefix in 'AC':
        shutil.copy2(scratch/(prefix+'B017.OUT'),HERE/'output'/(prefix+'_retry.txt'))
    shutil.copy2(scratch/'JUMP.OUT',HERE/'output/JUMP.txt')
    buf=io.StringIO(newline='')
    writer=csv.writer(buf,lineterminator='\n')
    writer.writerow(('program','case','year','month','invalid_lines','pass'))
    writer.writerows(rows)
    (HERE/'logs/输入测试.csv').write_text(buf.getvalue(),encoding='utf-8')
    failed=[k for k,v in checks.items() if not v]
    summary={'status':'FAIL' if failed else 'PASS','passed':sum(bool(v) for v in checks.values()),
        'total':len(checks),'calendar_months_per_program':2400,'input_runs':len(rows),
        'invalid_or_leading_zero_cases_per_program':len(invalid),'failed':failed,
        'checks':checks,'far_snapshots':[{k:f'{v:04X}' for k,v in s.items()} for s in snapshots],
        'c_functions':{f:{'offset':f'{csymbols[f]:04X}','bytes':size} for f,size in zip(funcs,sizes)},
        'sha256':{str(p.relative_to(HERE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                  for folder in ('src','bin') for p in (HERE/folder).iterdir() if p.is_file()}}
    (HERE/'验证结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('checks','sha256')},ensure_ascii=False,indent=2),flush=True)
    if failed:
        raise RuntimeError('Failed checks: '+str(failed))


if __name__=='__main__':
    main()
