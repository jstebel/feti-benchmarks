L = 1;
nx = 2;

Point(1) = { 0, 0, 0 };

Extrude{ L, 0, 0 }{ Point  { 1 }; Layers{ nx }; }
Extrude{ 0, L, 0 }{ Line   { 1 }; Layers{ nx }; }
Extrude{ 0, 0, L }{ Surface{ 5 }; Layers{ nx }; }

Physical Volume("domain") = { 1 };
Physical Surface(".top_z") = { 27 };
Physical Surface(".bottom_z") = { 5 };
Physical Surface(".front_y") = { 14 };
Physical Surface(".back_y") = { 22 };
Physical Surface(".left_x") = { 26 };
Physical Surface(".right_x") = { 18 };