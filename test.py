def second_wrapper(func):
    def wrapper():
        print('yay!')
        func()
    return wrapper

def first_wrapper(func):
    def wrapper():
        print('YAY!')
        func()
    return wrapper

@second_wrapper
@first_wrapper
def test_function():
    print('oh')

test_function()