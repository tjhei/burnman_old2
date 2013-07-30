#!/bin/bash

function testit {
t=$1
echo "*** testing $t ..."
(python <<EOF
import matplotlib as m
m.use('Cairo')
VERBOSE=1
execfile('$t')
EOF
)  >$t.tmp 2>&1 || { echo "test $t failed"; exit 1; } 
echo "diff $t.tmp misc/ref/$t.out"
diff $t.tmp misc/ref/$t.out || { echo "test $t failed"; exit 1; } 
rm $t.tmp
}




echo "*** running test suite..."
cd tests
python tests.py || exit 1
cd ..

python burnman/partitioning.py || exit 1

cd misc
echo "gen_doc..."
python gen_doc.py >/dev/null || exit 1
cd ..

testit "burnman/benchmark.py"
echo "   done"


echo ""

t="example_composition.py"
testit $t
#diff output_figures/example_composition.png misc/ref/example_composition.png || { echo "test $t failed"; exit 1; } 
echo "   done"

for test in `ls example*.py`
do
    [ $test == "example_inv_big_pv.py" ] && echo "*** skipping $test !" && continue
    [ $test == "example_inv_murakami.py" ] && echo "*** skipping $test !" && continue
    [ $test == "example_optimize_slb2011.py" ] && echo "*** skipping $test !" && continue
    [ $test == "example_premite_isothermal.py" ] && echo "*** skipping $test !" && continue
    [ $test == "example_spintransition.py" ] && echo "*** skipping $test !" && continue


    testit $test
    echo "   done"
done


testit "table.py"
echo "   done"



echo ""
echo "*** tests done"
