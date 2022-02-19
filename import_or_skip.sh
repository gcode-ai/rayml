# if there are more than 0 lines with importorskip, go into the if branch
if [ `grep -nR "importorskip" --include \*.py rayml/tests | wc -l | xargs` -ge 1 ]; then
    echo The following test files use importorskip. Refactor them to skip if has_minimal_dependencies is true
    echo or add the pytest.mark.noncore_dependency decorator.
    grep -nR "importorskip" --include \*.py rayml/tests
    exit 1
fi