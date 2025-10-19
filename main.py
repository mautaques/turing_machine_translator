# Tradutor de máquinas de turing para o projeto final da disciplina de Teoria da Computação
# Aluno: Mauricio Martins Taques Filho

from pathlib import Path
import argparse
import sys

def sipser_to_infinite(transitions):
    states = set()
    new_transitions = set()
    initial_state = 'initial_state'
    
    new_transitions.add('0 * * l 0')
    new_transitions.add('0 _ # r initial_state')
    
    for transition in transitions:
        current_state, current_symbol, new_symbol, direction, new_state = transition.split()
        
        if current_state == '0':
            current_state = initial_state
        if new_state == '0':
            new_state = initial_state
            
        states.add(current_state)
        states.add(new_state)
        
        new_transitions.add(f'{current_state} {current_symbol} {new_symbol} {direction} {new_state}')
    
    for state in states:
        new_transitions.add(f'{state} # * r {state}')
    
    return new_transitions

def infinite_to_sipser(transitions):
    states = set()
    symbols = set()
    new_transitions = set()
    initial_state = 'initial_state'
    
    new_transitions.add('0 0 # r rewrite_0')  
    new_transitions.add('0 1 # r rewrite_1')  
    new_transitions.add('rewrite_0 0 0 r rewrite_0')  
    new_transitions.add('rewrite_0 1 0 r rewrite_1')  
    new_transitions.add('rewrite_0 _ 0 r end_tape') 
    new_transitions.add('rewrite_1 1 1 r rewrite_1')  
    new_transitions.add('rewrite_1 0 1 r rewrite_0')  
    new_transitions.add('rewrite_1 _ 1 r end_tape') 
    new_transitions.add('end_tape _ + l end_tape')  
    new_transitions.add('end_tape * * l end_tape') 
    new_transitions.add('end_tape # * r initial_state') 
    
    
    for transition in transitions:
        current_state, current_symbol, new_symbol, direction, new_state = transition.split()
        
        if current_state == '0':
            current_state = initial_state
        if new_state == '0':
            new_state = initial_state
            
        states.add(current_state)
        states.add(new_state)
        symbols.add(current_symbol)
        symbols.add(new_symbol)
            
        if current_symbol == '_'  and direction == 'l':
            end_tape_state = 'end_tape_state_' + current_state
            new_transitions.add(f'{current_state} {current_symbol} {new_symbol} {direction} {new_state}')
            new_transitions.add(f'{current_state} + _ r {end_tape_state}')
            new_transitions.add(f'{end_tape_state} _ + l {current_state}')
            
        else:
            new_transitions.add(f'{current_state} {current_symbol} {new_symbol} {direction} {new_state}')
                
    for state in states:
        push_state = 'push_state' + state
        new_transitions.add(f'{state} # # r {push_state}')
        for from_symbol in symbols:
            from_rewrite_state = 'rewrite_state' + state + '_' + from_symbol
            new_transitions.add(f'{push_state} {from_symbol} _ r {from_rewrite_state}')
            for to_symbol in symbols:
                to_rewrite_state = 'rewrite_state' + state + '_' + to_symbol
                end_tape_state = 'end_state_' + state + '_+'
                goto_begin_state = 'goto_begin_state_' + state
                new_transitions.add(f'{from_rewrite_state} {to_symbol} {from_symbol} r {to_rewrite_state}')
                new_transitions.add(f'{from_rewrite_state} + {from_symbol} r {end_tape_state}')
                new_transitions.add(f'{end_tape_state} _ + l {goto_begin_state}')
                new_transitions.add(f'{goto_begin_state} * * l {goto_begin_state}')
                new_transitions.add(f'{goto_begin_state} # # r {state}')

    return new_transitions

def open_file(path, mode='r', encoding='utf-8'):
	p = Path(path)

	if not p.exists():
		raise FileNotFoundError(f"Nenhum arquivo passado como argumento: {p}")

	if p.suffix.lower() != '.in':
		raise ValueError(f"Extensão do arquivo deve ser '.in'")

	return open(p, mode, encoding=encoding)

def save_file(path, original_type, new_transitions):
    p_entrada = Path(path)
    output_path = p_entrada.with_suffix('.out') 
    
    new_header = ""
    if original_type == ";S":
        new_header = ";I"  # O novo arquivo é Semi-Standard
    else:
        new_header = ";S"  # O novo arquivo é Sipser

    with open(output_path, 'w') as file:
        file.write(new_header + "\n")
            
        for line in sorted(list(new_transitions)):
            file.write(line + "\n")
        
    print(f"\nArquivo traduzido salvo com sucesso em: {output_path}")

    
def main(argv=None):
    parser = argparse.ArgumentParser(description='Ler arquivo .in')
    parser.add_argument('path')
    
    args = parser.parse_args(argv)

    
    with open_file(args.path, 'r') as entry:
        type = entry.readline().rstrip('\n')
        transitions_list = entry.readlines() # Lê o resto do arquivo para uma lista

    translated_program = None
            
	# Verifica qual tipo de máquina de turing é
    if type == ';S':
        print("Traduzindo de Sipser para Semi Infinita...")
        translated_program = sipser_to_infinite(transitions_list)
    elif type == ';I':
        print("Traduzindo de Semi Infinita para Sipser...")
        translated_program = infinite_to_sipser(transitions_list)
    else:
        print(f"Tipo de MT desconhecido: '{type}", file=sys.stderr)
        return 1
            
    save_file(args.path, type, translated_program)
         

if __name__ == "__main__":
	raise SystemExit(main())
