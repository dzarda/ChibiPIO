
## What is this about?

We make ChibiOS independent of Makefiles, thus enabling its use in PlatformIO (or any other build system.) This is an experimental effort.

## How?

In advance, we selectively package sources relevant to your platform of choice. This is done by invoking `make lib -n` on maintained Makefiles. We parse the make stdout to obtain the list of files required.

Your job is to use the package zipped up for your MCU family and fill in the gaps:


## Usage
1. Get chconf.h, mcuconf.h and halconf.h (from *ChibiOS/os/{hal|rt}/templates*), edit for your needs, and place them so that they are seen by Chibi sources.
2. Get the linker script files (from *os\common\startup*)
3. Define linker symbols `__process_stack_size__`, `__main_stack_size__` to specify the size of stacks.

### Example platformio.ini

```ini
# platformio.ini
[platformio]

[env:myboard]
platform = ststm32
board_upload.maximum_size = 32768
board_build.ldscript = STM32fromchibios.ld
build_flags =
  ${env.build_flags}
  -Iinclude # Make sure Chibi sees our *conf.h files
  -Wl,--defsym=__process_stack_size__=0x400 # For the main() thread
  -Wl,--defsym=__main_stack_size__=0x200 # For ISRs

lib_deps =
  [tbd package URL]/ChibiPIO-STM32L0.zip

build_type = debug
extra_scripts =
  pre:pre_linker_specs.py

# pre_linker_specs.py
# Required for shrinking flash usage when we don't use "framework=cmsis"
Import("env")
env.Append(
    LINKFLAGS=[
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ]
)

```


## Notes

Some simplifications were made to get this up and running:
- ChibiOS/RT and ChibiOS/HAL are packaged together.
- Only GCC is supported (could be expanded, combinatorics though...)
- Only Cortex-M was considered.

Side effects compared to the Makefile solution:
- Support for each new platform must be explicitly added.
- Compile parameters (like `-fno-rtti`) normally specified in the ChibiOS Makefile are lost.
- "Smart build" functionality (where only relevant sources are compiled) is lost. This is a non-issue IMHO, Chibi sources are quick to compile nowadays.