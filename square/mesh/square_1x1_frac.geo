cl = 0.1;

Point(1) = { 0, 0, 0, cl };
Point(2) = { 1, 0, 0, cl };
Point(3) = { 1, 1, 0, cl };
Point(4) = { 0, 1, 0, cl };
Point(5) = { 0.25, 0.5, 0, cl };
Point(6) = { 0.75, 0.5, 0, cl };
Point(9) = { 0.75, 0.75, 0, cl };

Line(1) = { 1, 2 };
Line(2) = { 2, 3 };
Line(3) = { 3, 4 };
Line(4) = { 4, 1 };
Line(5) = { 5, 6 };

Line Loop(1) = { 1, 2, 3, 4 };
Plane Surface(1) = { 1 };

Line { 5 } In Surface { 1 };

Physical Line(".top") = { 3 };
Physical Line(".bottom") = { 1 };
Physical Line(".left") = { 4 };
Physical Line(".right") = { 2 };
Physical Line("fracture") = { 5 };
Physical Surface("rock") = { 1 };

