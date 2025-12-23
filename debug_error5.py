from src.core.services import Context

a = Context()
b = Context()

a.history.append("X")

print(a.history)
print(b.history)