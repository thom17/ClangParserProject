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