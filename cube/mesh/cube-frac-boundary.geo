SetFactory("OpenCASCADE");

L = 1;
nx = 5;

Point(1) = { -L/2, -L/2, -L/2, L/nx };

Extrude{ L, 0, 0 }{ Point  { 1 }; }
Extrude{ 0, L, 0 }{ Line   { 1 }; }
Extrude{ 0, 0, L }{ Surface{ 1 }; }

Disk(100) = { 0, 0, 0, L/3 };
//Rotate{ { 1, 2, 3 }, { 0, 0, 0 }, 2 }{ Surface{ 100 }; }
Translate{ 0, L/4, 0 }{ Surface{ 100 }; }

Disk(101) = { 0, 0, 0, L/3 };
Rotate{ { 1, 0, 0 }, { 0, 0, 0 }, Pi/4 }{ Surface{ 101 }; }

BooleanFragments{ Volume{ 1 }; Delete; }{ Surface{ 100, 101 }; Delete; }
Surface{ 101, 102, 104 } In Volume { 1 };

Physical Volume("domain") = { 1 };
Physical Surface("fractures") = { 101, 102, 104 };
Physical Surface(".top_z") = { 109 };
Physical Surface(".bottom_z") = { 108 };
Physical Surface(".front_y") = { 107 };
Physical Surface(".back_y") = { 106 };
Physical Surface(".left_x") = { 110 };
Physical Surface(".right_x") = { 105 };
Physical Line(".fractures") = { 4 };