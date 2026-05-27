SetFactory("OpenCASCADE");

L = 1;
nx = 5;

Point(1) = { -L/2, -L/2, -L/2, L/nx };

Extrude{ L, 0, 0 }{ Point  { 1 }; }
Extrude{ 0, L, 0 }{ Line   { 1 }; }
Extrude{ 0, 0, L }{ Surface{ 1 }; }

Disk(100) = { 0, 0, 0, L/3 };
Rotate{ { 1, 2, 3 }, { 0, 0, 0 }, 2 }{ Surface{ 100 }; }

Disk(101) = { 0, 0, 0, L/3 };
Rotate{ { 1, -2, 3 }, { 0, 0, 0 }, 2 }{ Surface{ 101 }; }

s() = BooleanFragments{ Surface{ 100 }; Delete; }{ Surface{ 101 }; Delete; };
Surface{ s() } In Volume { 1 };

Physical Volume("domain") = { 1 };
Physical Surface("fractures") = { s() };
Physical Surface(".top_z") = { 6 };
Physical Surface(".bottom_z") = { 1 };
Physical Surface(".front_y") = { 4 };
Physical Surface(".back_y") = { 5 };
Physical Surface(".left_x") = { 2 };
Physical Surface(".right_x") = { 3 };
//Physical Line("x") = { 14 };