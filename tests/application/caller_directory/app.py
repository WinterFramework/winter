from winter.application import Application

print(f'executing {__name__}')


class DefinedBeforeApplication:
    pass


app = Application()

if __name__ == '__main__':
    print(*(definition.__qualname__ for definition in app.definitions))
