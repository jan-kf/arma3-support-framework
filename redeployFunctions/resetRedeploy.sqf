//this addAction ["<t color='#FF0000'>Reset Redeploy</t>", "resetRedeploy.sqf", nil, 6, false, true, "", "true", 5, false, "", ""];

private _vic = _this select 0;
_vic setVariable ["performedReinsert", false, true];
_vic setVariable ["isReinserting", false, true];
_vic setVariable ["fallbackTriggered", false, true];