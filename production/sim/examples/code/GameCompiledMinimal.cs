using UnityEngine;

public class ModMeta : ModMetaBase
{
    public override string Name
    {
        get { return "SIM Example"; }
    }
}

public class ModBehaviour : ModBehaviourBase
{
    public override void OnActive()
    {
    }

    public override void OnDeactivate()
    {
    }
}
