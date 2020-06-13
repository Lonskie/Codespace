import turtle as t

t.shape('turtle')


def tree(pos, angle, depth=0):
    max_d = 8
    if depth >= max_d: return

    t.pencolor((angle % 361) / 360,
        depth / max_d,
        (max_d - depth) / max_d)

    t.pensize((max_d / (depth + 1))**1.2)
    t.speed(5 * depth / 3)

    t.penup()
    t.goto(pos)
    t.pendown()

    t.setheading(angle + 90)
    t.forward(100 * (1 - depth / max_d))

    root = t.position()
    change =  40 * (1 - depth / max_d)
    tree(root, angle + change, depth + 1)
    tree(root, angle - change, depth + 1)


tree((0, -200), 0)

t.penup()
t.speed(1)
t.goto(90, -170)
t.setheading(-90)

t.pendown()
t.pensize(3)
t.color(0.6, 1.0, 0.8)

# Draw 'L'
t.forward(40)
t.left(90)
t.forward(30)

# Letter space
t.penup()
t.forward(10)

# Draw 'E'
e_bottom = t.position()
t.pendown()
t.left(90)
t.forward(40)
t.right(90)
t.forward(30)
t.left(180)
t.forward(30)
t.left(90)
t.forward(20)
t.left(90)
t.forward(25)
t.penup()
t.goto(e_bottom)
t.pendown()
t.forward(30)

# Letter space
t.penup()
t.forward(10)

# Draw 'O'
t.pendown()
t.forward(30)
t.left(90)
t.forward(40)
t.left(90)
t.forward(30)
t.left(90)
t.forward(40)

# Letter space
t.left(90)
t.penup()
t.forward(40)

#Draw N
t.pendown()
t.left(90)
t.forward(40)
t.right(180 - 36.87)
t.forward(50)
t.setheading(90)
n_bottom_right = t.position()
t.forward(40)

# Full stop
t.penup()
t.goto(n_bottom_right)
t.setheading(0)
t.forward(20)
t.setheading(90)

t.exitonclick()