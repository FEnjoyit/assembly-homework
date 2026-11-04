"""Build with the course tools, then run DOS output and DEBUG checks."""
import argparse
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
ASM = ('H4TAB', 'H4CHK')
C = (('H4CTAB', 'H4TAB.C', []), ('H4CGLOB', 'H4CHK.C', []),
     ('H4CLOC', 'H4CHK.C', ['-dLOCAL_TABLE=1']))
BAD = {(1, 1), (2, 3), (4, 5), (6, 6), (8, 8)}
COORDS = [(x, y) for x in range(1, 10) for y in range(1, 10)]
GOOD_TABLE = bytes(x*y for x, y in COORDS)
BAD_TABLE = bytes(7 if (x, y) in BAD else x*y for x, y in COORDS)


def dos_text(path, text):
    path.write_bytes(text.replace('\r\n', '\n').replace('\n', '\r\n').encode('ascii'))


def table_output():
    lines = ['The 9mul9 table:']
    for x in range(9, 0, -1):
        terms = [f'{x}*{y}={x*y}' for y in range(1, x+1)]
        lines.append(''.join(term.ljust(8) for term in terms[:-1]) + terms[-1])
    return ('\r\n'.join(lines) + '\r\n').encode('ascii')


def checker_output(coords):
    return ('x y\r\n' + ''.join(f'{x} {y}   error\r\n' for x, y in sorted(coords))
            + '\r\naccomplish!\r\n').encode('ascii')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-root', type=Path, default=HERE.parents[1])
    course = parser.parse_args().course_root.resolve()
    work, scratch = course/'dos/work', course/'dos/tests/H4'
    scratch.mkdir(parents=True, exist_ok=True)
    (course/'tmp').mkdir(exist_ok=True)
    for p in sorted((HERE/'src').iterdir()):
        if p.suffix.upper() in ('.ASM', '.INC', '.C', '.BAT'):
            dos_text(work/p.name, p.read_text(encoding='ascii'))

    def read(path):
        return path.read_text(encoding='cp437')

    def launch(tag, lines):
        batch = 'H4' + tag + '.BAT'
        dos_text(scratch/batch, '\n'.join(['@echo off', 'cd \\work'] + lines) + '\n')
        config = course/'tmp'/('H4' + tag + '.conf')
        config.write_bytes((course/'dosbox-course.conf').read_bytes() +
                           f'\r\ncall d:\\tests\\h4\\{batch}\r\nexit\r\n'.encode('ascii'))
        env = os.environ.copy()
        env.pop('SDL_VIDEODRIVER', None)
        env.pop('SDL_AUDIODRIVER', None)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        result = subprocess.run([str(course/'tools/dosbox-x/dosbox-x.exe'), '-noconsole',
                                 '-conf', str(config)], cwd=scratch, env=env,
                                startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW,
                                timeout=50, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(result.stdout.decode('cp437', errors='replace'))

    def finish(lines, name):
        marker = scratch/name
        marker.unlink(missing_ok=True)
        return lines + [f'echo PASS > d:\\tests\\h4\\{name}', 'goto end',
                        ':fail', f'echo FAIL > d:\\tests\\h4\\{name}', ':end']

    def require_marker(name):
        marker = scratch/name
        if not marker.exists() or read(marker).strip() != 'PASS':
            raise RuntimeError(f'DOS batch failed; see {scratch}')

    lines = []
    checks = {}
    for stem in ASM:
        lines.extend([f'masm {stem}.ASM,{stem}.OBJ,{stem}.LST; > d:\\tests\\h4\\A{stem[2:]}.LOG',
                      'if errorlevel 1 goto fail',
                      f'link {stem}.OBJ,{stem}.EXE,{stem}.MAP; > d:\\tests\\h4\\L{stem[2:]}.LOG',
                      'if errorlevel 1 goto fail'])
    launch('BUILD', finish(lines, 'BUILD.OK'))
    require_marker('BUILD.OK')
    for stem in ASM:
        asm_log = read(scratch/f'A{stem[2:]}.LOG')
        link_log = read(scratch/f'L{stem[2:]}.LOG')
        checks[stem+'_build'] = (bool(re.search(r'0\s+Warning Errors', asm_log)) and
                                 bool(re.search(r'0\s+Severe\s+Errors', asm_log)) and
                                 not re.search(r'\b(?:error|warning)\b', link_log, re.I))

    watcom = course/'tools/watcom'
    env = {**os.environ, 'WATCOM':str(watcom), 'INCLUDE':str(watcom/'h'),
           'PATH':str(watcom/'binnt') + os.pathsep + os.environ.get('PATH','')}
    options = ['-0','-ms','-bt=dos','-l=dos','-od','-d2','-s','-w=4','-we']
    mains = {}
    for stem, source, extra in C:
        compile_log = subprocess.run([str(watcom/'binnt/wcl.exe'), *options, *extra,
                                       f'-fe={stem}.EXE',f'-fo={stem}.OBJ',f'-fm={stem}.MAP',source],
                                      cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                      timeout=40)
        (scratch/(stem+'.LOG')).write_bytes(compile_log.stdout)
        if compile_log.returncode:
            raise RuntimeError(compile_log.stdout.decode('cp437'))
        dis = subprocess.run([str(watcom/'binnt/wdis.exe'),f'-s={source}',f'-l={stem}.TXT',stem+'.OBJ'],
                             cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
        if dis.returncode:
            raise RuntimeError(dis.stdout.decode('cp437'))
        listing = read(work/(stem+'.TXT'))
        mapping = read(work/(stem+'.MAP'))
        size = int(re.search(r'Routine Size:\s*(\d+) bytes',listing)[1])
        main_at = int(re.search(r'\b[0-9A-F]+:([0-9A-F]+)\s+main_',mapping)[1],16)
        mains[stem] = {'offset':f'{main_at:04X}','bytes':size}
        checks[stem+'_build'] = (b'0 warnings, 0 errors' in compile_log.stdout and
                                 'USE16' in listing and 'No disassembly errors' in listing)

    def label(stem, name):
        listing=read(work/(stem+'.LST'))
        return int(re.search(r'^\s*([0-9A-F]{4})\s+(?:C\s+)?'+name+r':',listing,re.M)[1],16)

    start, pad, ret = (label('H4TAB', n) for n in ('COL_LOOP','TERM_PAD','TERM_RETURN'))
    chk_start, chk_inner, chk_ret = ((label('H4CHK', n)) for n in ('COL_LOOP','PD_WRITE','CELL_RETURN'))
    scripts = {
        'H4TAB':f'tm 1\ng=0 {start:x}\nr\nt\ng {pad:x}\nr\ng {ret:x}\nr\ng\nq\n',
        'H4CHK':f'tm 1\ng=0 {chk_start:x}\nr\nt\ng {chk_inner:x}\nr\ng {chk_ret:x}\nr\ng\nq\n',
    }
    for stem, m in mains.items():
        scripts[stem]=f'r\nu cs:{m["offset"]} l{m["bytes"]:x}\ng {m["offset"]}\nr\ng\nq\n'
    lines = []
    stems = ASM + tuple(stem for stem, _, _ in C)
    for stem in stems:
        exe = (work/(stem+'.EXE')).read_bytes()
        checks[stem+'_dos_exe'] = exe[:2] == b'MZ'
        lines.extend([f'{stem} > d:\\tests\\h4\\{stem}.OUT', 'if errorlevel 1 goto fail'])
        dos_text(scratch/(stem+'.IN'), scripts[stem])
        lines.append(f'debug {stem}.EXE < d:\\tests\\h4\\{stem}.IN > d:\\tests\\h4\\{stem}.DBG')

    # Replace only the unique embedded table in temporary copies of the EXEs.
    # Each case starts with the correct table and changes exactly one byte to 0.
    cases = []
    for prefix, stem in zip('AGL', ('H4CHK','H4CGLOB','H4CLOC')):
        original=(work/(stem+'.EXE')).read_bytes()
        if original.count(BAD_TABLE)!=1:
            raise RuntimeError(f'Expected one embedded 81-byte fixture in {stem}')
        for n in range(82):
            fixture=bytearray(GOOD_TABLE)
            coords=[]
            if n:
                fixture[n-1]=0
                coords=[COORDS[n-1]]
            case=f'{prefix}{n:03d}'
            (scratch/(case+'.EXE')).write_bytes(original.replace(BAD_TABLE, bytes(fixture), 1))
            lines.extend([f'd:\\tests\\h4\\{case}.EXE > d:\\tests\\h4\\{case}.OUT',
                          'if errorlevel 1 goto fail'])
            cases.append((case,stem,coords))
    launch('RUN',finish(lines,'RUN.OK'))
    require_marker('RUN.OK')

    for stem in stems:
        output=(scratch/(stem+'.OUT')).read_bytes()
        expected=table_output() if stem in ('H4TAB','H4CTAB') else checker_output(BAD)
        checks[stem+'_exact_output']=output==expected
        log=read(scratch/(stem+'.DBG'))
        checks[stem+'_debug_exit'] = ('Program terminated normally (0000)' in log and
                                      not re.search(r'\^\s*error\b|syntax error|file not found',log,re.I))
    for stem in mains:
        log=read(scratch/(stem+'.DBG'))
        checks[stem+'_main_breakpoint']=f'IP={mains[stem]["offset"]}' in log

    def state(stem, ip, **registers):
        log=read(scratch/(stem+'.DBG'))
        for first, second in re.findall(r'^(AX=.*)\n(DS=.*)$',log,re.M):
            pairs=dict(re.findall(r'([A-Z]{2})=([0-9A-F]{4})',first+' '+second))
            if pairs.get('IP')==f'{ip:04X}' and all(pairs.get(k)==v for k,v in registers.items()):
                return True
        return False

    checks['print_term_borrows_and_restores_cx'] = (
        state('H4TAB',start,BX='0009',CX='0009',SI='0001',SP='0100') and
        state('H4TAB',pad,BX='0009',CX='0003',SI='0001',SP='00F8') and
        state('H4TAB',ret,BX='0009',CX='0009',SI='0001',SP='0100'))
    checks['check_cell_nested_registers_restored'] = (
        state('H4CHK',chk_start,BX='0001',CX='0009',SI='0001',DI='0000',SP='0100') and
        state('H4CHK',chk_inner,BX='000A',CX='0001',SI='0001',DI='0000') and
        state('H4CHK',chk_ret,BX='0001',CX='0009',SI='0001',DI='0000',SP='0100'))
    rows=[]
    for case,stem,coords in cases:
        output=(scratch/(case+'.OUT')).read_bytes()
        detected=re.findall(rb'(?m)^([1-9]) ([1-9])   error\r$',output)
        ok=output==checker_output(coords)
        checks[case]=ok
        expected=';'.join(f'{x}:{y}' for x,y in coords)
        actual=';'.join(f'{x.decode()}:{y.decode()}' for x,y in detected)
        rows.append((case,stem,expected,actual,ok))
    failed=[k for k,v in checks.items() if not v]
    if failed:
        print('Failed checks:',failed)
        for stem in stems:
            if stem+'_exact_output' in failed:
                print(stem,repr((scratch/(stem+'.OUT')).read_bytes()))
        raise SystemExit(1)

    for folder in ('bin','logs','output'):
        (HERE/folder).mkdir(exist_ok=True)
    for stem in stems:
        shutil.copy2(work/(stem+'.EXE'),HERE/'bin'/(stem+'.EXE'))
        for suffix in ('.LST','.MAP','.TXT'):
            p=work/(stem+suffix)
            if p.is_file(): shutil.copy2(p,HERE/'logs'/p.name)
        for suffix in ('.DBG','.IN'):
            shutil.copy2(scratch/(stem+suffix),HERE/'logs'/(stem+suffix))
        shutil.copy2(scratch/(stem+'.OUT'),HERE/'output'/(stem+'.txt'))
    for name in ('ATAB.LOG','LTAB.LOG','ACHK.LOG','LCHK.LOG','H4CTAB.LOG','H4CGLOB.LOG','H4CLOC.LOG'):
        shutil.copy2(scratch/name,HERE/'logs'/name)
    csv_text=io.StringIO(newline='')
    writer=csv.writer(csv_text,lineterminator='\n')
    writer.writerow(('case','program','expected_row_col','actual_row_col','pass'))
    writer.writerows(rows)
    (HERE/'logs/逐格测试.csv').write_text(csv_text.getvalue(),encoding='utf-8')
    summary={'status':'PASS','passed':len(checks),'total':len(checks),
             'table_terms':45,'checker_cells':81,'checker_error_coordinates':sorted(BAD),
             'checker_variants':3,'isolated_cell_cases':243,'clean_table_cases':3,
             'c_main':mains,
             'sha256':{f'{p.parent.name}/{p.name}':hashlib.sha256((work/p.name).read_bytes()).hexdigest()
                       for folder in ('src','bin') for p in sorted((HERE/folder).iterdir())
                       if p.is_file() and p.suffix.upper() in ('.ASM','.C','.INC','.EXE')}}
    (HERE/'验证结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
