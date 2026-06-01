class Heap:
    def __init__(self, heap_type="min"):
        self.arr = []
        self.type = heap_type

    def parent(self, i): return (i - 1) // 2
    def left(self, i): return 2 * i + 1
    def right(self, i): return 2 * i + 2

    def compare(self, child, parent):
        if self.type == "min":
            return self.arr[child] < self.arr[parent]
        return self.arr[child] > self.arr[parent]

    def build_heap_instant(self, values):
        self.arr = []
        for v in values:
            self.arr.append(v)
            curr = len(self.arr) - 1
            while curr > 0 and self.compare(curr, self.parent(curr)):
                p = self.parent(curr)
                self.arr[curr], self.arr[p] = self.arr[p], self.arr[curr]
                curr = p

    def convert_heap_gen(self, new_type):
        self.type = new_type
        n = len(self.arr)
        for i in range(n // 2 - 1, -1, -1):
            yield from self.heapify_down_gen(i, n)

    def heapify_down_gen(self, i, n):
        extreme = i
        l, r = self.left(i), self.right(i)
        if l < n and self.compare(l, extreme): extreme = l
        if r < n and self.compare(r, extreme): extreme = r
        if extreme != i:
            yield (i, extreme) 
            self.arr[i], self.arr[extreme] = self.arr[extreme], self.arr[i]
            yield from self.heapify_down_gen(extreme, n)

    def delete_node_gen(self, index):
        n = len(self.arr)
        if index < 0 or index >= n:
            return

        last_index = n - 1

        yield ("fade", index) 

        if index != last_index:
            yield ("move", last_index, index)
            self.arr[index] = self.arr[last_index]

        self.arr.pop()

        if index < len(self.arr):
            parent_idx = self.parent(index)
            if index > 0 and self.compare(index, parent_idx):
                yield from self.heapify_up_gen(index)
            else:
                yield from self.heapify_down_gen(index, len(self.arr))

    def heapify_up_gen(self, i):
        while i > 0:
            p = self.parent(i)
            if self.compare(i, p):
                yield (i, p)
                self.arr[i], self.arr[p] = self.arr[p], self.arr[i]
                i = p
            else:
                break