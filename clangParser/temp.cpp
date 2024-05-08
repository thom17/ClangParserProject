void GetImplantInfo(CModuleDocAPImplantSimulation * pModuleDoc)
{
	tinyxml2::XMLElement* pElRoot = CTinyXMLWrapper::FirstChildElement(&_docResult, IMPLANT_ROOT_ELEMENT);
	ASSERT(pElRoot);

	int nIndex = 0;

	ST_IMPLANT_STYLE* pImplantStyle = new ST_IMPLANT_STYLE;

	tinyxml2::XMLElement* pElStyle = CTinyXMLWrapper::FirstChildElement(pElRoot, IMPLANT_SAFETY);
	while (pElStyle)
	{
		ST_SAFETY_STLYE structSafety;

		tinyxml2::XMLElement* pElRadical = CTinyXMLWrapper::FirstChildElement(pElStyle, IMPLANT_RADICAL);
		if (pElRadical)
		{
			CString strRadical;
			CTinyXMLWrapper::GetText(pElRadical, strRadical);
			structSafety.nRadialDistance = _ttoi(strRadical);
		}

		tinyxml2::XMLElement* pElApical = CTinyXMLWrapper::FirstChildElement(pElStyle, IMPLANT_APICAL);
		if (pElApical)
		{
			CString strApical;
			CTinyXMLWrapper::GetText(pElApical, strApical);
			structSafety.nApicalDistance = _ttoi(strApical);
		}

		tinyxml2::XMLElement* pElRemove = CTinyXMLWrapper::FirstChildElement(pElStyle, IMPLANT_REMOVE);
		if (pElRemove)
		{
			CString strRemove;
			CTinyXMLWrapper::GetText(pElRemove, strRemove);

			if (0 == strRemove.Compare(L"true"))
				structSafety.bRemove = true;
			else
				structSafety.bRemove = false;
		}

		pImplantStyle->vSafety[nIndex] = structSafety;
		++nIndex;

		pElStyle = CTinyXMLWrapper::NextSiblingElement(pElStyle, IMPLANT_SAFETY);
	}

	pModuleDoc->SetImplantInfo(*pImplantStyle);

	pImplantStyle->vSafety.clear();
	SAFE_DELETE(pImplantStyle);
}