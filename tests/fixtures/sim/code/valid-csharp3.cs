using System;

public class Sample
{
    public Func<int, int> Double()
    {
        return x => x * 2;
    }
}
