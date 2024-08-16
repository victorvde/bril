var r: bigint = fibonacci(20n);
console.log(r);

function fibonacci(x: bigint) : bigint {
    var acc: bigint = 0n;
    var prev: bigint = 0n;
    var cur: bigint = 1n;
    for(var i: bigint = 0n; i < x; i = i + 1n) {
        var temp: bigint = prev + cur;
        prev = cur;
        cur = temp;
    }

    return prev;
}
