bool OnUpdate(UINT nId, WPARAM wParam, const CUpdateParam* pParam, const LPVOID pSender)
{
	// base operation
	bool bRes = __super::OnUpdate(nId, wParam, pParam, pSender);

	// VR������ opacity curve�� object �Ӽ����� ����Ǿ����� �˸��� �̺�Ʈ�� ó���ؾ� �Ѵ�.
	UNREFERENCED_PARAMETER(wParam);
	UNREFERENCED_PARAMETER(pParam);

	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// �ڱ� �ڽ��� ���� �޽����� ó���ϴ� ���.
	if (pSender == this)
	{
	}
	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// ���� ���� �޽����� ó���ϴ� ���.On
	else
	{
	}

	CLocalDocAP* pLocalDoc = reinterpret_cast<CLocalDocAP*>(GetLocalDoc());
	
	if (nId == BUM::BUM_MODULE_FIXTURE_UPDATE_COLOR)
	{
		if (GetLogStep()) ProcLogRcvStep(nId);
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);
		//RedrawActuator();	//MakeImage�� �����ϰ� �ٽ� �׸���.  
		bRes = true;	//������ ������ �׸��� ���� MakeImage �ʿ� 
	}
	else if (nId == BUM::BUM_MODULE_PANO_CS_POS_CHANGED	// �ĳ�� ������ CS Position(Sampling Point)�� ����� ���
		|| nId == BUM::BUM_MODULE_PLANE_CS_ROTATED	// CS PLANE ȸ������ CS Position ���� ���� ������ ����� ���
		|| nId == BUM::BUM_MODULE_PLANE_TGT_ROTATED	// Tgt PLANE ȸ������ CS Position ���� ���� ������ ����� ���
		)
	{
		if (GetLogStep()) ProcLogRcvStep(nId);
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);

		auto pDSItemCSPos = dynamic_cast<CDSICSPositioning*>(LookupDSI(DSI_NAME_PANO_CS_POS, 0)); 
		auto pDsipanoAxial = dynamic_cast<CDSIPanoAxialPlane*>(LookupDSI(DSI_NAME_PANO_AXIAL, 0));
		auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul));
		
		//#4072 �������� �׻� �ʿ��ҵ� 
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
		//�ϴ� ��ü ���� ���� ����
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
	////CActuatorAxialFixture�� ctrl + Mouse Wheel
	//else if(nId == BUM::BUM_MODULE_PANO_HORIZONTAL_LINE_CHANGED_BY_MOUSEWHEEL)
	//{
	//	CalPanoActImgAndCsInfo();

	//	_updateDsiRelatedPano();
	//}
	//
	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// Sender�� ������� �׻� ó���ؾ� �ϴ� ���.
	if (nId == BUM::BUM_MODULE_DENTAL_ARCH_CHANGED || nId == BUM::BUM_MODULE_HORIZONTAL_LINE_CHANGED)
	{
if (GetLogStep()) ProcLogRcvStep(nId); 
else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);
		CLocalDocAP* pLocalDoc = reinterpret_cast<CLocalDocAP*>(GetLocalDoc());
		if (E_APSteps::APStep_FixtureImplantation == pLocalDoc->GetCurrentStep())
		{
			auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul));
			
			if (MoudleDoc->GetUseCS())	//CSLine�� ����ϴ� ��쿡�� ���
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
