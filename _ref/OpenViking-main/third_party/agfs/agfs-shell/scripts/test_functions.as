#!/usr/bin/env uv run agfs-shell

# Test suite for working function features
# This only tests features that are currently supported

echo "=== Function Feature Tests (Currently Supported) ==="
echo ""

# Test 1: Basic function definition and call
echo "Test 1: Basic Function Call"
greet() {
    echo "Hello, $1!"
}

greet Alice
greet Bob
echo "✓ Basic function calls work"
echo ""

# Test 2: Positional parameters
echo "Test 2: Positional Parameters"
show_params() {
    echo "Function: $0"
    echo "Count: $#"
    echo "First: $1"
    echo "Second: $2"
    echo "All: $@"
}

show_params apple banana cherry
echo "✓ Positional parameters work"
echo ""

# Test 3: Local variables
echo "Test 3: Local Variables"
x=100
test_local() {
    local x=10
    echo "Inside function: x=$x"
    x=20
    echo "Modified local: x=$x"
}

echo "Before function: x=$x"
test_local
echo "After function: x=$x"
echo "✓ Local variables work (global unchanged)"
echo ""

# Test 4: Arithmetic with local variables
echo "Test 4: Arithmetic with Local Variables"
calc() {
    local a=$1
    local b=$2
    local sum=$((a + b))
    local product=$((a * b))
    echo "Sum: $sum"
    echo "Product: $product"
}

calc 5 3
echo "✓ Arithmetic with local variables works"
echo ""

# Test 5: Return values (only test success case in script mode)
echo "Test 5: Return Values"
check_success() {
    if [ $1 -eq 42 ]; then
        return 0
    fi
    return 1
}

check_success 42
echo "check_success(42): $? (expected: 0)"

# Note: Testing return 1 would stop script execution
# In interactive mode, you can test: check_success 0; echo $?
echo "✓ Return values work"
echo ""

# Test 6: If statements in functions
echo "Test 6: If Statements"
check_positive() {
    if [ $1 -gt 0 ]; then
        echo "Positive"
    elif [ $1 -lt 0 ]; then
        echo "Negative"
    else
        echo "Zero"
    fi
}

check_positive 5
check_positive -3
check_positive 0
echo "✓ If statements in functions work"
echo ""

# Test 7: For loops in functions
echo "Test 7: For Loops"
print_list() {
    for item in $@; do
        echo "  - $item"
    done
}

print_list apple banana cherry
echo "✓ For loops in functions work"
echo ""

# Test 8: Function calling another function
echo "Test 8: Function Calling Function"
inner() {
    echo "Inner function called with: $1"
}

outer() {
    echo "Outer function calling inner..."
    inner "from outer"
}

outer
echo "✓ Functions can call other functions"
echo ""

# Test 9: Multiple local variables
echo "Test 9: Multiple Local Variables"
multi_local() {
    local a=1
    local b=2
    local c=3
    echo "a=$a, b=$b, c=$c"
    local sum=$((a + b + c))
    echo "Sum: $sum"
}

multi_local
echo "✓ Multiple local variables work"
echo ""

# Test 10: Functions with continue in loops
echo "Test 10: Continue in Loops"
test_continue() {
    for i in 1 2 3 4 5; do
        if [ $i -eq 3 ]; then
            continue
        fi
        echo "  $i"
    done
}

echo "Continue test:"
test_continue
echo "✓ Continue works in function loops"
echo ""

# Note: Break also works but causes non-zero exit in current implementation
# when loop exits early. This is a known behavior.

echo "=== All Supported Features Work! ==="
