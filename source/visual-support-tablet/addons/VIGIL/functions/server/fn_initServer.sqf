/*
Hail, Holy Queen, Mother of Mercy,
our life, our sweetness, and our hope.
To thee do we cry,
poor banished children of Eve.
To thee do we send up our sighs,
mourning and weeping in this valley of tears.
Turn then, most gracious advocate,
thine eyes of mercy toward us,
and after this our exile
show unto us the blessed fruit of
thy womb, Jesus.
O clement, O loving,
O sweet Virgin Mary. Amen.
*/

if (!isServer) exitWith {};

[] call YSF_governorStart;

YSF_helicopterStab_pfhSecondId = [YSF_helicopterStab_perSecond, 1, nil] call CBA_fnc_addPerFrameHandler;