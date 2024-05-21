#include <iostream>
int SetToothFixtureNumberList(int listToothFixtureNumber)
{
    std::vector<int> listUpper;
	std::vector<int> listLower;

	for (auto nTooth : listToothFixtureNumber)
	{
		if (31 > nTooth)
		{
			listUpper.push_back(nTooth);
		}
		else
		{
			listLower.push_back(nTooth);
		}
	}

    return 0;
}
