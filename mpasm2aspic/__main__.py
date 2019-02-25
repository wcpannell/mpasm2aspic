from sys import argv
import mpasm2aspic
from mpasm2aspic.pic16f877 import INSTRUCTION_SET


def main(infile="", outfile=None, instruction_set=INSTRUCTION_SET):
    print(infile, outfile)
    Pic = mpasm2aspic.Parser(instruction_set)
    out_lines = []
    with open(infile) as f:
        for line in f:
            tokens = Pic.parse(line)
            out_lines.append(Pic.textify(tokens))
    if outfile is None and infile[-1] != "S":
        outfile = ".".join(infile.split(".")[:-1]) + ".S"
    with open(outfile, "w") as f:
        for line in out_lines:
            f.write(line + "\n")


if len(argv) == 4:
    if argv[3] != "PIC16F887":
        print(argv[3], "is not implemented")
    else:
        main(*argv[1:2])
elif 2 <= len(argv) < 4:
    main(*argv[1:])
else:
    print("Arguments:")
    print(
        "python -m mpasm2aspic input_mpasm_file.asm output_mpasm_file.S \
        PIC16F8877"
    )
