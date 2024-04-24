bool OnUpdate(UINT nId, WPARAM wParam, const CUpdateParam* pParam, const LPVOID pSender)
{
	// base operation
	bool bRes = __super::OnUpdate(nId, wParam, pParam, pSender);

	// VR영상의 opacity curve나 object 속성등이 변경되었음을 알리는 이벤트를 처리해야 한다.
	UNREFERENCED_PARAMETER(wParam);
	UNREFERENCED_PARAMETER(pParam);

	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// 자기 자신이 보낸 메시지만 처리하는 경우.
	if (pSender == this)
	{
	}
	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// 남이 보낸 메시지만 처리하는 경우.On
	else
	{
	}

	CLocalDocAP* pLocalDoc = reinterpret_cast<CLocalDocAP*>(GetLocalDoc());
	
	if (nId == BUM::BUM_MODULE_FIXTURE_UPDATE_COLOR)
	{
		if (GetLogStep()) ProcLogRcvStep(nId);
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);
		//RedrawActuator();	//MakeImage는 제외하고 다시 그린다.  
		bRes = true;	//렌더러 측에서 그리기 위해 MakeImage 필요 
	}
	else if (nId == BUM::BUM_MODULE_PANO_CS_POS_CHANGED	// 파노라마 영상의 CS Position(Sampling Point)이 변경된 경우
		|| nId == BUM::BUM_MODULE_PLANE_CS_ROTATED	// CS PLANE 회전으로 CS Position 관련 벡터 정보가 변경된 경우
		|| nId == BUM::BUM_MODULE_PLANE_TGT_ROTATED	// Tgt PLANE 회전으로 CS Position 관련 벡터 정보가 변경된 경우
		)
	{
		if (GetLogStep()) ProcLogRcvStep(nId);
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);

		auto pDSItemCSPos = dynamic_cast<CDSICSPositioning*>(LookupDSI(DSI_NAME_PANO_CS_POS, 0)); 
		auto pDsipanoAxial = dynamic_cast<CDSIPanoAxialPlane*>(LookupDSI(DSI_NAME_PANO_AXIAL, 0));
		auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul));
		
		//#4072 수직선은 항상 필요할듯 
		if (MoudleDoc->GetUseCS())
		{
			pDSItemCSPos->EnableDSI(true);
			//pDsipanoAxial->SetVisible(true);
		}
		else
		{
			pDSItemCSPos->EnableDSI(false);
			//pDsipanoAxial->SetVisible(false);
		}

		if (pLocalDoc->GetPanoAxialEvent())
			_bUpdate = true;
		else bRes = true;

		LOGN_(System) << " < MsgComp > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);
	}

	else if (nId == BUM::BUM_MODULE_FIXTURE_HYBRID_MANIPULATOR_TRANSFORM)
	{
		if (GetLogStep()) ProcLogRcvStep(nId);
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);

		auto pDSItemCSPos = dynamic_cast<CDSICSPositioning*>(LookupDSI(DSI_NAME_PANO_CS_POS, 0));
		pDSItemCSPos->EnableDSI(false);
	}

	else if (nId == BUM::BUM_UPDATE_PROC)
	{
USE_FUTURE
		if (GetLogStep()) ProcLogRcvStep(nId);
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);

		if (_bUpdate)
		bRes = true;

		_bUpdate = false;

END_FUTURE
	}
	else if (nId == BUM::BUM_COMMON_EACH_TOOTH_SELECT)
	{
		//일단 전체 갱신 추후 정리
		pLocalDoc->GetWritablePanoInfo()->SetNeedChngPanoForAllStep(true);

		auto pDSI = (CDSILibraryDrawer*)LookupDSI(DSI_NAME_PANO_IMP_LIB_DRAWER, 0);
		//pDSI->clearRecord();

		auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul));
		MoudleDoc->SetUseCS(false);
		CalPanoActImgAndCsInfo();

		_updateDsiRelatedPano();

		if (pLocalDoc->GetPanoAxialEvent())
			_bUpdate = true;
		else bRes = true;

		LOGN_(System) << " < MsgComp > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);
	}
	////CActuatorAxialFixture의 ctrl + Mouse Wheel
	//else if(nId == BUM::BUM_MODULE_PANO_HORIZONTAL_LINE_CHANGED_BY_MOUSEWHEEL)
	//{
	//	CalPanoActImgAndCsInfo();

	//	_updateDsiRelatedPano();
	//}
	//
	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// Sender에 상관없이 항상 처리해야 하는 경우.
	if (nId == BUM::BUM_MODULE_DENTAL_ARCH_CHANGED || nId == BUM::BUM_MODULE_HORIZONTAL_LINE_CHANGED)
	{
if (GetLogStep()) ProcLogRcvStep(nId); 
else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);
		CLocalDocAP* pLocalDoc = reinterpret_cast<CLocalDocAP*>(GetLocalDoc());
		if (E_APSteps::APStep_FixtureImplantation == pLocalDoc->GetCurrentStep())
		{
			auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul));
			
			if (MoudleDoc->GetUseCS())	//CSLine을 사용하는 경우에만 계산
				CalPanoActImgAndCsInfo();
		
			_updateDsiRelatedPano();
			if (pLocalDoc->GetPanoAxialEvent())
				_bUpdate = true;
			else bRes = true;
		}
		LOGN_(System) << " < MsgComp > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);
	}
	
	return bRes;
}
