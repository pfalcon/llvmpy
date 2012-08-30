from llvm.core import *
from llvm.passes import *
from llvm.ee import *
from llvm_cbuilder import *
import llvm_cbuilder.shortnames as C
import sys, unittest, logging
from subprocess import Popen, PIPE

def gen_debugprint(mod):
    functype = Type.function(C.void, [])
    func = mod.add_function(functype, 'debugprint')

    cb = CBuilder(func)
    fmt = cb.constant_string("Show %d %.3f %.3e\n")

    an_int = cb.constant(C.int, 123)
    a_float = cb.constant(C.double, 1.234)
    a_double = cb.constant(C.double, 1e-31)
    cb.printf(fmt, an_int, a_float, a_double)

    cb.debug('an_int =', an_int, 'a_float =', a_float, 'a_double =', a_double)

    cb.ret()
    cb.close()
    return func

def main_debugprint():
    # generate code
    mod = Module.new(__name__)
    lfunc = gen_debugprint(mod)
    logging.debug(mod)
    mod.verify()
    # run
    exe = CExecutor(mod)
    func = exe.get_ctype_function(lfunc, 'void')
    func()

class TestPrint(unittest.TestCase):
    def test_debugprint(self):
        p = Popen(["python", __file__, "-child"], stdout=PIPE)
        p.wait()

        lines = p.stdout.read().decode().splitlines(False)

        expect = [
            'Show 123 1.234 1.000e-31',
            'an_int = 123 a_float = 1.234000e+00 a_double = 1.000000e-31',
            ]
        self.assertEqual(expect, lines)

        p.stdout.close()

if __name__ == '__main__':
    try:
        if sys.argv[1] == '-child':
            main_debugprint()
    except IndexError:
        unittest.main()


