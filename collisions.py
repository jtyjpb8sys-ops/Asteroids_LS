def point_in_triangle(p, tri) -> bool:
    a, b, c = tri
    def sign(p1, p2, p3):
        return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
    d1 = sign(p, a, b)
    d2 = sign(p, b, c)
    d3 = sign(p, c, a)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)

def segment_distance(p, a, b) -> float:
    ab = b - a
    if ab.length_squared() == 0:
        return p.distance_to(a)
    t = max(0, min(1, (p - a).dot(ab) / ab.length_squared()))
    closest = a + ab * t
    return p.distance_to(closest)

def circle_triangle_collision(center, radius, tri) -> bool:
    for v in tri:
        if center.distance_to(v) <= radius:
            return True

    if point_in_triangle(center, tri):
        return True
    
    for i in range(3):
        a, b = tri[i], tri[(i + 1) % 3]
        if segment_distance(center, a, b) <= radius:
            return True
    return False