def even_numbers(limit):
    n = 0
    while n <= limit:
        yield n
        print("Incrementing")
        n += 2

# Example usage:
limit = 10
even_gen = even_numbers(limit)
print(even_gen)
for num in even_gen:
    print(num)
