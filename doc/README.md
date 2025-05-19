# Specs

### Components structure

```
src/  
│  
├── main.py                     # Entry point: runs the simulation  
├── config.py                   # Global config: resolution, memory sizes, etc.  
│  
├── screen/  
│   └── screen.py               # Stores and displays raw pixels  
│  
├── device/  
│   ├── keyboard.py             # Simulated keyboard (event queue or polling)  
│   ├── disk.py                 # Simulated disk or storage  
│   └── timer.py                # Optional clock or interrupt time  
│  
├── cpu/  
│   ├── vm.py                   # Virtual CPU core: registers, instructions  
│   └── isa.py                  # Instruction definitions / encoding  
│  
├── memory/  
│   ├── ram.py                  # RAM abstraction: read/write by address  
│   └── rom.py                  # Boot ROM or preloaded instructions  
│  
├── os/  
│   ├── monitor.py              # Basic OS or bootloader  
│   └── syscalls.py             # Print text, read key, etc.  
│  
├── assembler/  
│   └── assembler.py            # Turns assembly into bytecode for the VM  
│  
├── util/  
│   ├── colors.py               # Color utilities  
│   └── compute_backend.py      # CPU/GPU computation module  
│  
└── programs/  
    └── hello.asm               # Sample assembly program  
```
