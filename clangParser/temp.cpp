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

void run(int a, int b)
{
    __supper::run(a, b);
}

bool OnUpdate(UINT nId, WPARAM wParam, const CUpdateParam * pParam, const LPVOID pSender)
{
	bool bRes = false;
	UNREFERENCED_PARAMETER(nId);
	UNREFERENCED_PARAMETER(pParam);
	UNREFERENCED_PARAMETER(pSender);
	if (nId == BUM::BUM_COMMON_CROSS_SECTION_SHOW_DATA)
	{

		_bDrawText = false;
		bRes = true;
	}

	else if (nId == BUM::BUM_COMMON_SHOW_2D)
	{
USE_FUTURE


		int nShow = (int)wParam;
		if (nShow == 1) {
			_fZoomFactor = 3.0f;
			//_pCamera->SetZoomFactor(fDefaultZoom);
			_pCamera->SetFrontView();
			_bDrawText = true;
			_pEye = m_pCoordConv->GetEye();
		}
		else if (nShow == 2) {
			_bToothChange = true;
		}

		bRes = true;

END_FUTURE
	}
	else if (nId == BUM::BUM_COMMON_SIDESLIDER_CHANGED)
	{

		bRes = true;
	}

	return bRes;
}