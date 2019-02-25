An assembly converter for updating your old/legacy/new-but-oh-crap-it-won't-play-nicely-with-xc8 Microchip MPASM assembly to Microchip xc8 Assembly (ASPIC).

-------------------
What's the problem?
-------------------
   xc8 still honors the Instruction set in the datasheets (with some exceptions), and the register definition names are largely the same in each assemblers' include files. So where's the issue? By line count, the most trouble is in the handling of literals. For example MPASM wants RETLW B'01010101', where xc8 wants RETLW 01010101b. There are also some differences between Macros (i.e. MESSG("Your message shown during assembly" has no equavilent in xc8).

-----------
Why Bother?
-----------
   I maintain a large legacy codebase written in MPASM. I'd like to be able to port it entirely to C at some point in the future, but spending months to years replacing known good code with new bugs just won't fly. xc8 will allow me to split up the assembly, replace it with C whenever I need to touch it, and hopefully, be able to ensure matching output when desired

-----------
How to use?
-----------
   Clone this repository and cd to it. Have poetry installed as a system package. Type poetry run python -m mpasm2aspic inputfilepath outputfilepath instructionset.

   You could also import mpasm2aspic and use the Parser class. See mpasm2aspic/__main__.py for how to use it.

