// Added by sckim, on 2018/10/17.
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include "stdafx.h"
#include "ActuatorPanoFixture.h"

#include "../BaseTools/plogger.h"
#include "../AppFrame/VolumeDoc.h"
#ifdef _DEBUG
#define new DEBUG_NEW
#endif
#include "../AppFrame/SideSliderDoc.h"
#include "../Doitinterface/RayIntersection.h"
#include "ModuleDocAPImplantSimulation.h"

#include "../AppCommon_AP/DSICSPositioning.h"
#include "../AppCommon_AP/DSIPanoAxialPlane.h"
#include <chrono>

#include "DSILibraryDrawer.h"

#define AND	&&
#define NOT	!


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// macro constants


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// constructor
CActuatorPanoFixture::CActuatorPanoFixture() // CONSTRUCTOR(CActuatorPanoFixture) // TYPE_REF(class CActuatorPanoFixture)
	: CActuatorPanoNerveBase(NAME_ACTUATOR_FIXTURE_PANO, true) // TYPE_REF(class CActuatorPanoNerveBase) // CALL_EXPR(CActuatorPanoNerveBase) // UNEXPOSED_EXPR() // STRING_LITERAL(L"ACTUATOR_FIXTURE_PANO") // CXX_BOOL_LITERAL_EXPR()
{ // COMPOUND_STMT() // CXX_OVERRIDE_ATTR()
}
 // CXX_OVERRIDE_ATTR()

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// // CXX_OVERRIDE_ATTR()
// destructor
CActuatorPanoFixture::~CActuatorPanoFixture() // DESTRUCTOR(~CActuatorPanoFixture) // TYPE_REF(class CActuatorPanoFixture) // CXX_OVERRIDE_ATTR()
{ // COMPOUND_STMT()
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Process update messages and broadcast to child message target item. // CXX_OVERRIDE_ATTR()
//auto-gen-future
#include <future>
#define USE_FUTURE auto updateFuture = std::async(std::launch::async, [nId, wParam, pParam, pSender, &bRes, pLocalDoc,this](){ // CXX_OVERRIDE_ATTR()
#define END_FUTURE });updateFuture.wait();
bool CActuatorPanoFixture::OnUpdate(UINT nId, WPARAM wParam, const CUpdateParam* pParam, const LPVOID pSender) // CXX_METHOD(OnUpdate) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(nId) // TYPE_REF(UINT) // PARM_DECL(wParam) // TYPE_REF(WPARAM) // PARM_DECL(pParam) // TYPE_REF(class CUpdateParam) // PARM_DECL(pSender) // TYPE_REF(LPVOID)
{ // COMPOUND_STMT()
	// base operation
	bool bRes = __super::OnUpdate(nId, wParam, pParam, pSender); // DECL_STMT() // VAR_DECL(bRes) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnUpdate) // DECL_REF_EXPR(nId) // DECL_REF_EXPR(wParam) // DECL_REF_EXPR(pParam) // DECL_REF_EXPR(pSender)

	// VR영상의 opacity curve나 object 속성등이 변경되었음을 알리는 이벤트를 처리해야 한다.
	UNREFERENCED_PARAMETER(wParam); // PAREN_EXPR() // DECL_REF_EXPR(wParam)
	UNREFERENCED_PARAMETER(pParam); // PAREN_EXPR() // DECL_REF_EXPR(pParam)

	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// 자기 자신이 보낸 메시지만 처리하는 경우.
	if (pSender == this) // IF_STMT() // BINARY_OPERATOR() // UNEXPOSED_EXPR(pSender) // DECL_REF_EXPR(pSender) // UNEXPOSED_EXPR() // CXX_THIS_EXPR()
	{ // COMPOUND_STMT()
	}
	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// 남이 보낸 메시지만 처리하는 경우.On
	else
	{ // COMPOUND_STMT()
	}

	CLocalDocAP* pLocalDoc = reinterpret_cast<CLocalDocAP*>(GetLocalDoc()); // DECL_STMT() // VAR_DECL(pLocalDoc) // TYPE_REF(class CLocalDocAP) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CLocalDocAP) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDoc)
	
	if (nId == BUM::BUM_MODULE_FIXTURE_UPDATE_COLOR) // IF_STMT() // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_MODULE_FIXTURE_UPDATE_COLOR) // DECL_REF_EXPR(BUM_MODULE_FIXTURE_UPDATE_COLOR) // NAMESPACE_REF(BUM)
	{ // COMPOUND_STMT()
		if (GetLogStep()) ProcLogRcvStep(nId); // IF_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLogStep) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ProcLogRcvStep) // DECL_REF_EXPR(nId)
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId); // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(LOGN_) // DECL_REF_EXPR(System) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" < RcvMsg > ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL("(") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // MEMBER_REF_EXPR(_strName) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(")") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CSTYLE_CAST_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ConEventMessage) // DECL_REF_EXPR(nId)
		//RedrawActuator();	//MakeImage는 제외하고 다시 그린다.  
		bRes = true;	//렌더러 측에서 그리기 위해 MakeImage 필요  // BINARY_OPERATOR() // DECL_REF_EXPR(bRes) // CXX_BOOL_LITERAL_EXPR()
	}
	else if (nId == BUM::BUM_MODULE_PANO_CS_POS_CHANGED	// 파노라마 영상의 CS Position(Sampling Point)이 변경된 경우 // IF_STMT() // BINARY_OPERATOR() // BINARY_OPERATOR() // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_MODULE_PANO_CS_POS_CHANGED) // DECL_REF_EXPR(BUM_MODULE_PANO_CS_POS_CHANGED) // NAMESPACE_REF(BUM)
		|| nId == BUM::BUM_MODULE_PLANE_CS_ROTATED	// CS PLANE 회전으로 CS Position 관련 벡터 정보가 변경된 경우 // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_MODULE_PLANE_CS_ROTATED) // DECL_REF_EXPR(BUM_MODULE_PLANE_CS_ROTATED) // NAMESPACE_REF(BUM)
		|| nId == BUM::BUM_MODULE_PLANE_TGT_ROTATED	// Tgt PLANE 회전으로 CS Position 관련 벡터 정보가 변경된 경우 // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_MODULE_PLANE_TGT_ROTATED) // DECL_REF_EXPR(BUM_MODULE_PLANE_TGT_ROTATED) // NAMESPACE_REF(BUM)
		)
	{ // COMPOUND_STMT()
		if (GetLogStep()) ProcLogRcvStep(nId); // IF_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLogStep) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ProcLogRcvStep) // DECL_REF_EXPR(nId)
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId); // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(LOGN_) // DECL_REF_EXPR(System) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" < RcvMsg > ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL("(") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // MEMBER_REF_EXPR(_strName) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(")") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CSTYLE_CAST_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ConEventMessage) // DECL_REF_EXPR(nId)

		auto pDSItemCSPos = dynamic_cast<CDSICSPositioning*>(LookupDSI(DSI_NAME_PANO_CS_POS, 0));  // DECL_STMT() // VAR_DECL(pDSItemCSPos) // CXX_DYNAMIC_CAST_EXPR() // TYPE_REF(class CDSICSPositioning) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_PANO_CS_POS") // INTEGER_LITERAL()
		auto pDsipanoAxial = dynamic_cast<CDSIPanoAxialPlane*>(LookupDSI(DSI_NAME_PANO_AXIAL, 0)); // DECL_STMT() // VAR_DECL(pDsipanoAxial) // CXX_DYNAMIC_CAST_EXPR() // TYPE_REF(class CDSIPanoAxialPlane) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_PANO_AXIAL") // INTEGER_LITERAL()
		auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul)); // DECL_STMT() // VAR_DECL(MoudleDoc) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CModuleDocAPImplantSimulation) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // DECL_REF_EXPR(APMod_ImplantSimul)
		
		//#4072 수직선은 항상 필요할듯 
		if (MoudleDoc->GetUseCS()) // IF_STMT() // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(MoudleDoc)
		{ // COMPOUND_STMT()
			pDSItemCSPos->EnableDSI(true); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSItemCSPos) // CXX_BOOL_LITERAL_EXPR()
			//pDsipanoAxial->SetVisible(true);
		}
		else
		{ // COMPOUND_STMT()
			pDSItemCSPos->EnableDSI(false); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSItemCSPos) // CXX_BOOL_LITERAL_EXPR()
			//pDsipanoAxial->SetVisible(false);
		}

		if (pLocalDoc->GetPanoAxialEvent()) // IF_STMT() // CALL_EXPR(GetPanoAxialEvent) // MEMBER_REF_EXPR(GetPanoAxialEvent) // UNEXPOSED_EXPR(pLocalDoc) // DECL_REF_EXPR(pLocalDoc)
			_bUpdate = true; // BINARY_OPERATOR() // MEMBER_REF_EXPR(_bUpdate) // CXX_BOOL_LITERAL_EXPR()
		else bRes = true; // BINARY_OPERATOR() // DECL_REF_EXPR(bRes) // CXX_BOOL_LITERAL_EXPR()

		LOGN_(System) << " < MsgComp > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId); // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(LOGN_) // DECL_REF_EXPR(System) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" < MsgComp > ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL("(") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // MEMBER_REF_EXPR(_strName) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(")") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CSTYLE_CAST_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ConEventMessage) // DECL_REF_EXPR(nId)
	}

	else if (nId == BUM::BUM_MODULE_FIXTURE_HYBRID_MANIPULATOR_TRANSFORM) // IF_STMT() // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_MODULE_FIXTURE_HYBRID_MANIPULATOR_TRANSFORM) // DECL_REF_EXPR(BUM_MODULE_FIXTURE_HYBRID_MANIPULATOR_TRANSFORM) // NAMESPACE_REF(BUM)
	{ // COMPOUND_STMT()
		if (GetLogStep()) ProcLogRcvStep(nId); // IF_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLogStep) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ProcLogRcvStep) // DECL_REF_EXPR(nId)
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId); // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(LOGN_) // DECL_REF_EXPR(System) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" < RcvMsg > ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL("(") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // MEMBER_REF_EXPR(_strName) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(")") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CSTYLE_CAST_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ConEventMessage) // DECL_REF_EXPR(nId)

		auto pDSItemCSPos = dynamic_cast<CDSICSPositioning*>(LookupDSI(DSI_NAME_PANO_CS_POS, 0)); // DECL_STMT() // VAR_DECL(pDSItemCSPos) // CXX_DYNAMIC_CAST_EXPR() // TYPE_REF(class CDSICSPositioning) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_PANO_CS_POS") // INTEGER_LITERAL()
		pDSItemCSPos->EnableDSI(false); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSItemCSPos) // CXX_BOOL_LITERAL_EXPR()
	}

	else if (nId == BUM::BUM_UPDATE_PROC) // IF_STMT() // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_UPDATE_PROC) // DECL_REF_EXPR(BUM_UPDATE_PROC) // NAMESPACE_REF(BUM)
	{ // COMPOUND_STMT()
USE_FUTURE // DECL_STMT() // VAR_DECL(updateFuture)
		if (GetLogStep()) ProcLogRcvStep(nId);
		else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId);

		if (_bUpdate)
		bRes = true;

		_bUpdate = false;

END_FUTURE // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(updateFuture)
	}
	else if (nId == BUM::BUM_COMMON_EACH_TOOTH_SELECT) // IF_STMT() // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_COMMON_EACH_TOOTH_SELECT) // DECL_REF_EXPR(BUM_COMMON_EACH_TOOTH_SELECT) // NAMESPACE_REF(BUM)
	{ // COMPOUND_STMT()
		_bNeedDrawCT = true; // BINARY_OPERATOR() // MEMBER_REF_EXPR(_bNeedDrawCT) // CXX_BOOL_LITERAL_EXPR()

		auto pDSI = (CDSILibraryDrawer*)LookupDSI(DSI_NAME_PANO_IMP_LIB_DRAWER, 0); // DECL_STMT() // VAR_DECL(pDSI) // CSTYLE_CAST_EXPR() // TYPE_REF(class CDSILibraryDrawer) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_MODEL_DRAWER") // INTEGER_LITERAL()
		//pDSI->clearRecord();

		auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul)); // DECL_STMT() // VAR_DECL(MoudleDoc) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CModuleDocAPImplantSimulation) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // DECL_REF_EXPR(APMod_ImplantSimul)
		MoudleDoc->SetUseCS(false); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(MoudleDoc) // CXX_BOOL_LITERAL_EXPR()
		CalPanoActImgAndCsInfo(); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(CalPanoActImgAndCsInfo)

		_updateDsiRelatedPano(); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(_updateDsiRelatedPano)

		if (pLocalDoc->GetPanoAxialEvent()) // IF_STMT() // CALL_EXPR(GetPanoAxialEvent) // MEMBER_REF_EXPR(GetPanoAxialEvent) // UNEXPOSED_EXPR(pLocalDoc) // DECL_REF_EXPR(pLocalDoc)
			_bUpdate = true; // BINARY_OPERATOR() // MEMBER_REF_EXPR(_bUpdate) // CXX_BOOL_LITERAL_EXPR()
		else bRes = true; // BINARY_OPERATOR() // DECL_REF_EXPR(bRes) // CXX_BOOL_LITERAL_EXPR()

		LOGN_(System) << " < MsgComp > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId); // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(LOGN_) // DECL_REF_EXPR(System) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" < MsgComp > ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL("(") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // MEMBER_REF_EXPR(_strName) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(")") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CSTYLE_CAST_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ConEventMessage) // DECL_REF_EXPR(nId)
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
	if (nId == BUM::BUM_MODULE_DENTAL_ARCH_CHANGED || nId == BUM::BUM_MODULE_HORIZONTAL_LINE_CHANGED) // IF_STMT() // BINARY_OPERATOR() // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_MODULE_DENTAL_ARCH_CHANGED) // DECL_REF_EXPR(BUM_MODULE_DENTAL_ARCH_CHANGED) // NAMESPACE_REF(BUM) // BINARY_OPERATOR() // UNEXPOSED_EXPR(nId) // DECL_REF_EXPR(nId) // UNEXPOSED_EXPR(BUM_MODULE_HORIZONTAL_LINE_CHANGED) // DECL_REF_EXPR(BUM_MODULE_HORIZONTAL_LINE_CHANGED) // NAMESPACE_REF(BUM)
	{ // COMPOUND_STMT()
if (GetLogStep()) ProcLogRcvStep(nId);  // IF_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLogStep) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ProcLogRcvStep) // DECL_REF_EXPR(nId)
else LOGN_(System) << " < RcvMsg > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId); // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(LOGN_) // DECL_REF_EXPR(System) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" < RcvMsg > ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL("(") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // MEMBER_REF_EXPR(_strName) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(")") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CSTYLE_CAST_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ConEventMessage) // DECL_REF_EXPR(nId)
		CLocalDocAP* pLocalDoc = reinterpret_cast<CLocalDocAP*>(GetLocalDoc()); // DECL_STMT() // VAR_DECL(pLocalDoc) // TYPE_REF(class CLocalDocAP) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CLocalDocAP) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDoc)
		if (E_APSteps::APStep_FixtureImplantation == pLocalDoc->GetCurrentStep()) // IF_STMT() // CALL_EXPR() // DECL_REF_EXPR(APStep_FixtureImplantation) // TYPE_REF(enum E_APSteps) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator==) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetCurrentStep) // UNEXPOSED_EXPR(pLocalDoc) // DECL_REF_EXPR(pLocalDoc)
		{ // COMPOUND_STMT()
			auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul)); // DECL_STMT() // VAR_DECL(MoudleDoc) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CModuleDocAPImplantSimulation) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // DECL_REF_EXPR(APMod_ImplantSimul)
			
			if (MoudleDoc->GetUseCS())	//CSLine을 사용하는 경우에만 계산 // IF_STMT() // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(MoudleDoc)
				CalPanoActImgAndCsInfo(); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(CalPanoActImgAndCsInfo)
		
			_updateDsiRelatedPano(); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(_updateDsiRelatedPano)
			if (pLocalDoc->GetPanoAxialEvent()) // IF_STMT() // CALL_EXPR(GetPanoAxialEvent) // MEMBER_REF_EXPR(GetPanoAxialEvent) // UNEXPOSED_EXPR(pLocalDoc) // DECL_REF_EXPR(pLocalDoc)
				_bUpdate = true; // BINARY_OPERATOR() // MEMBER_REF_EXPR(_bUpdate) // CXX_BOOL_LITERAL_EXPR()
			else bRes = true; // BINARY_OPERATOR() // DECL_REF_EXPR(bRes) // CXX_BOOL_LITERAL_EXPR()
		}
		LOGN_(System) << " < MsgComp > " << "(" << _strName << ")" << " : " << (const wchar_t*)ConEventMessage(nId); // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(LOGN_) // DECL_REF_EXPR(System) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" < MsgComp > ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL("(") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // MEMBER_REF_EXPR(_strName) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(")") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CSTYLE_CAST_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(ConEventMessage) // DECL_REF_EXPR(nId)
	}
	
	return bRes; // RETURN_STMT() // UNEXPOSED_EXPR(bRes) // DECL_REF_EXPR(bRes)
}

void CActuatorPanoFixture::OnInitialUpdate(void) // CXX_METHOD(OnInitialUpdate) // TYPE_REF(class CActuatorPanoFixture)
{ // COMPOUND_STMT()
	__super::OnInitialUpdate(); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnInitialUpdate)

	auto pDSI = (CDSILibraryDrawer*)LookupDSI(DSI_NAME_PANO_IMP_LIB_DRAWER, 0); // DECL_STMT() // VAR_DECL(pDSI) // CSTYLE_CAST_EXPR() // TYPE_REF(class CDSILibraryDrawer) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_MODEL_DRAWER") // INTEGER_LITERAL()

	if (pDSI == nullptr) // IF_STMT() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSI) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator==) // CXX_NULL_PTR_LITERAL_EXPR()
	{ // COMPOUND_STMT()
		pDSI = new CDSILibraryDrawer(DSI_NAME_PANO_IMP_LIB_DRAWER, this, GetLocalDocAP(), true); // BINARY_OPERATOR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSI) // CXX_NEW_EXPR() // TYPE_REF(class CDSILibraryDrawer) // UNEXPOSED_EXPR() // STRING_LITERAL(L"DSI_MODEL_DRAWER") // CXX_THIS_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // CXX_BOOL_LITERAL_EXPR()
		pDSI->setRenderer(_pImgRenderer); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSI) // MEMBER_REF_EXPR(_pImgRenderer)
		AddDSI(pDSI); // CALL_EXPR(AddDSI) // MEMBER_REF_EXPR(AddDSI) // UNEXPOSED_EXPR()
	}
	auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul)); // DECL_STMT() // VAR_DECL(MoudleDoc) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CModuleDocAPImplantSimulation) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // DECL_REF_EXPR(APMod_ImplantSimul)
	MoudleDoc->SetUseCS(false); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(MoudleDoc) // CXX_BOOL_LITERAL_EXPR()


	pDSI->clearRecord(); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSI)
	pDSI->setRenderer(_pImgRenderer); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSI) // MEMBER_REF_EXPR(_pImgRenderer)
	//pDSI->setCenterPanoActImgInfo(GetCenterPanoActImgInfo());

	//CLocalDocAP* pLocalDoc = reinterpret_cast<CLocalDocAP*>(GetLocalDoc());
	//if (E_APSteps::APStep_FixtureImplantation == pLocalDoc->GetCurrentStep())
	//{
	//	CalPanoActImgAndCsInfo();

	//	_updateDsiRelatedPano();
	//}
}

#include "../AppCommon_AP/DSICSPositioning.h"
#include "../AppCommon_AP/DSIPanoAxialPlane.h"

bool CActuatorPanoFixture::OnActLBDown(UINT nFlags, CPoint point) // CXX_METHOD(OnActLBDown) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(nFlags) // TYPE_REF(UINT) // PARM_DECL(point) // TYPE_REF(class CPoint)
{ // COMPOUND_STMT()
	auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul)); // DECL_STMT() // VAR_DECL(MoudleDoc) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CModuleDocAPImplantSimulation) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // DECL_REF_EXPR(APMod_ImplantSimul)
	if (MoudleDoc->GetUseCS()) // IF_STMT() // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(MoudleDoc)
		return __super::OnActLBDown(nFlags, point); // RETURN_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnActLBDown) // DECL_REF_EXPR(nFlags) // DECL_REF_EXPR(point)
	else
	{ // COMPOUND_STMT()
		//이전 위치로 (3Shape 기준) 
		auto pDsiCSPos = dynamic_cast<CDSICSPositioning*>(LookupDSI(DSI_NAME_PANO_CS_POS, 0)); // DECL_STMT() // VAR_DECL(pDsiCSPos) // CXX_DYNAMIC_CAST_EXPR() // TYPE_REF(class CDSICSPositioning) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_PANO_CS_POS") // INTEGER_LITERAL()
		if (pDsiCSPos) // IF_STMT() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDsiCSPos)
			point.x = pDsiCSPos->GetPanoScreenX(); // BINARY_OPERATOR() // MEMBER_REF_EXPR(x) // UNEXPOSED_EXPR(point) // DECL_REF_EXPR(point) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR()

		return __super::OnActLBDown(nFlags, point); // RETURN_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnActLBDown) // DECL_REF_EXPR(nFlags) // DECL_REF_EXPR(point)
}
}

bool CActuatorPanoFixture::OnActMouseMove(UINT nFlags, CPoint point) // CXX_METHOD(OnActMouseMove) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(nFlags) // TYPE_REF(UINT) // PARM_DECL(point) // TYPE_REF(class CPoint)
{ // COMPOUND_STMT()
	auto MoudleDoc = reinterpret_cast<CModuleDocAPImplantSimulation*>(GetLocalDocAP()->GetWritableModuleDoc(APMod_ImplantSimul)); // DECL_STMT() // VAR_DECL(MoudleDoc) // CXX_REINTERPRET_CAST_EXPR() // TYPE_REF(class CModuleDocAPImplantSimulation) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // DECL_REF_EXPR(APMod_ImplantSimul)
	if (MoudleDoc->GetUseCS()) // IF_STMT() // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(MoudleDoc)
		return __super::OnActMouseMove(nFlags, point); // RETURN_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnActMouseMove) // DECL_REF_EXPR(nFlags) // DECL_REF_EXPR(point)
	else
	{ // COMPOUND_STMT()
		//이전 위치로 (3Shape 기준) 
		auto pDsiCSPos = dynamic_cast<CDSICSPositioning*>(LookupDSI(DSI_NAME_PANO_CS_POS, 0)); // DECL_STMT() // VAR_DECL(pDsiCSPos) // CXX_DYNAMIC_CAST_EXPR() // TYPE_REF(class CDSICSPositioning) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_PANO_CS_POS") // INTEGER_LITERAL()
		if (pDsiCSPos) // IF_STMT() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDsiCSPos)
			point.x = pDsiCSPos->GetPanoScreenX(); // BINARY_OPERATOR() // MEMBER_REF_EXPR(x) // UNEXPOSED_EXPR(point) // DECL_REF_EXPR(point) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR()

		return __super::OnActMouseMove(nFlags, point); // RETURN_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnActMouseMove) // DECL_REF_EXPR(nFlags) // DECL_REF_EXPR(point)
	}

}
bool CActuatorPanoFixture::OnActRBDown(UINT nFlags, CPoint point) // CXX_METHOD(OnActRBDown) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(nFlags) // TYPE_REF(UINT) // PARM_DECL(point) // TYPE_REF(class CPoint)
{ // COMPOUND_STMT()
	if(LookupDSI(DSI_NAME_PANO_IMP_LIB_DRAWER , 0) == nullptr) // IF_STMT() // CALL_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_MODEL_DRAWER") // INTEGER_LITERAL() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator==) // CXX_NULL_PTR_LITERAL_EXPR()
		AddDSI(new CDSILibraryDrawer(DSI_NAME_PANO_IMP_LIB_DRAWER, this, GetLocalDocAP(), false)); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(AddDSI) // CXX_NEW_EXPR() // TYPE_REF(class CDSILibraryDrawer) // UNEXPOSED_EXPR() // STRING_LITERAL(L"DSI_MODEL_DRAWER") // CXX_THIS_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP) // CXX_BOOL_LITERAL_EXPR()

	return __super::OnActRBDown(nFlags, point); // RETURN_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnActRBDown) // DECL_REF_EXPR(nFlags) // DECL_REF_EXPR(point)
}

bool CActuatorPanoFixture::OnActMouseWheel(UINT nFlags, short zDelta, CPoint point) // CXX_METHOD(OnActMouseWheel) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(nFlags) // TYPE_REF(UINT) // PARM_DECL(zDelta) // PARM_DECL(point) // TYPE_REF(class CPoint)
{ // COMPOUND_STMT()
	return __super::OnActMouseWheel(nFlags, zDelta, point); // RETURN_STMT() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(OnActMouseWheel) // DECL_REF_EXPR(nFlags) // DECL_REF_EXPR(zDelta) // DECL_REF_EXPR(point)
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// TitleBar를 memory dc에 그린다.
void CActuatorPanoFixture::DrawTitleBar(CDC* pDC) // CXX_METHOD(DrawTitleBar) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(pDC) // TYPE_REF(class CDC)
{ // COMPOUND_STMT()
	CRect rcTemp; // DECL_STMT() // VAR_DECL(rcTemp) // TYPE_REF(class CRect) // CALL_EXPR(CRect)
	::GetClientRect(GetParentPaneHwnd(), rcTemp); // CALL_EXPR(GetClientRect) // DECL_REF_EXPR(GetClientRect) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetParentPaneHwnd) // DECL_REF_EXPR(rcTemp)

	Gdiplus::Graphics graphics(pDC->GetSafeHdc()); // DECL_STMT() // VAR_DECL(graphics) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Graphics) // CALL_EXPR(Graphics) // CALL_EXPR(GetSafeHdc) // MEMBER_REF_EXPR(GetSafeHdc) // UNEXPOSED_EXPR(pDC) // UNEXPOSED_EXPR(pDC) // DECL_REF_EXPR(pDC)
	Gdiplus::SolidBrush br(Gdiplus::Color(178, 89, 101, 139)); // DECL_STMT() // VAR_DECL(br) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::SolidBrush) // UNEXPOSED_EXPR() // CALL_EXPR(SolidBrush) // UNEXPOSED_EXPR() // UNEXPOSED_EXPR(Color) // CALL_EXPR(Color) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Color) // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL()
	graphics.FillRectangle(&br, 0, 0, rcTemp.Width(), TITLE_BAR_HEIGHT); // CALL_EXPR(FillRectangle) // MEMBER_REF_EXPR(FillRectangle) // DECL_REF_EXPR(graphics) // UNEXPOSED_EXPR() // UNARY_OPERATOR() // DECL_REF_EXPR(br) // INTEGER_LITERAL() // INTEGER_LITERAL() // CALL_EXPR(Width) // MEMBER_REF_EXPR(Width) // UNEXPOSED_EXPR(rcTemp) // DECL_REF_EXPR(rcTemp) // INTEGER_LITERAL()
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Text overlay를 memory dc에 그린다.
void CActuatorPanoFixture::DrawTextOverlay(CDC* pDC) // CXX_METHOD(DrawTextOverlay) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(pDC) // TYPE_REF(class CDC)
{ // COMPOUND_STMT()
	UNREFERENCED_PARAMETER(pDC); // PAREN_EXPR() // DECL_REF_EXPR(pDC)

	Gdiplus::Graphics* pGraphic = BitmapUtils::GetGDIplusGraphics(pDC); // DECL_STMT() // VAR_DECL(pGraphic) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Graphics) // CALL_EXPR(GetGDIplusGraphics) // UNEXPOSED_EXPR(GetGDIplusGraphics) // DECL_REF_EXPR(GetGDIplusGraphics) // TYPE_REF(class BitmapUtils) // UNEXPOSED_EXPR(pDC) // DECL_REF_EXPR(pDC)
	ASSERT(pGraphic); // PAREN_EXPR() // CSTYLE_CAST_EXPR() // INTEGER_LITERAL()

	// 글자색/그림자색은 디자이너와 상의한 값. 추후 option 처리 해야 함.
	Gdiplus::Color clrText = Gdiplus::Color::MakeARGB(255, 135, 241, 255); // DECL_STMT() // VAR_DECL(clrText) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Color) // UNEXPOSED_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // UNEXPOSED_EXPR(Color) // CALL_EXPR(Color) // CALL_EXPR(MakeARGB) // UNEXPOSED_EXPR(MakeARGB) // DECL_REF_EXPR(MakeARGB) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Color) // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL()
	Gdiplus::Color clrShadow = Gdiplus::Color::MakeARGB(225, 10, 15, 30); // DECL_STMT() // VAR_DECL(clrShadow) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Color) // UNEXPOSED_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // UNEXPOSED_EXPR(Color) // CALL_EXPR(Color) // CALL_EXPR(MakeARGB) // UNEXPOSED_EXPR(MakeARGB) // DECL_REF_EXPR(MakeARGB) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Color) // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL()
	Gdiplus::SolidBrush brush(clrText); // DECL_STMT() // VAR_DECL(brush) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::SolidBrush) // CALL_EXPR(SolidBrush) // UNEXPOSED_EXPR(clrText) // DECL_REF_EXPR(clrText)
	Gdiplus::SolidBrush brushShadow(clrShadow); // DECL_STMT() // VAR_DECL(brushShadow) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::SolidBrush) // CALL_EXPR(SolidBrush) // UNEXPOSED_EXPR(clrShadow) // DECL_REF_EXPR(clrShadow)

	const Gdiplus::Font font(L"Tahoma", 11, Gdiplus::FontStyleBold); // DECL_STMT() // VAR_DECL(font) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::Font) // CALL_EXPR(Font) // UNEXPOSED_EXPR() // STRING_LITERAL(L"Tahoma") // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR(FontStyleBold) // DECL_REF_EXPR(FontStyleBold) // NAMESPACE_REF(Gdiplus)
	const float fTextGap = 11; // DECL_STMT() // VAR_DECL(fTextGap) // UNEXPOSED_EXPR() // INTEGER_LITERAL()

	CString strName = StringTable::Ready(L"PANORAMA"); // DECL_STMT() // VAR_DECL(strName) // TYPE_REF(CString) // UNEXPOSED_EXPR() // DECL_REF_EXPR(Ready) // TYPE_REF(class StringTable) // STRING_LITERAL(L"PANORAMA")

	// Patient name (with shadow)
	Gdiplus::StringFormat strFormat; // DECL_STMT() // VAR_DECL(strFormat) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::StringFormat) // CALL_EXPR(StringFormat)
	strFormat.SetAlignment(Gdiplus::StringAlignmentNear); // CALL_EXPR(SetAlignment) // MEMBER_REF_EXPR(SetAlignment) // DECL_REF_EXPR(strFormat) // DECL_REF_EXPR(StringAlignmentNear) // NAMESPACE_REF(Gdiplus)
	strFormat.SetLineAlignment(Gdiplus::StringAlignmentNear); // CALL_EXPR(SetLineAlignment) // MEMBER_REF_EXPR(SetLineAlignment) // DECL_REF_EXPR(strFormat) // DECL_REF_EXPR(StringAlignmentNear) // NAMESPACE_REF(Gdiplus)
	Gdiplus::PointF ptString((Gdiplus::REAL)fTextGap + 1, (Gdiplus::REAL)5); // DECL_STMT() // VAR_DECL(ptString) // NAMESPACE_REF(Gdiplus) // TYPE_REF(class Gdiplus::PointF) // CALL_EXPR(PointF) // BINARY_OPERATOR() // CSTYLE_CAST_EXPR() // NAMESPACE_REF(Gdiplus) // TYPE_REF(Gdiplus::REAL) // UNEXPOSED_EXPR(fTextGap) // DECL_REF_EXPR(fTextGap) // UNEXPOSED_EXPR() // INTEGER_LITERAL() // CSTYLE_CAST_EXPR() // NAMESPACE_REF(Gdiplus) // TYPE_REF(Gdiplus::REAL) // UNEXPOSED_EXPR() // INTEGER_LITERAL()
	pGraphic->DrawString(strName, -1, &font, ptString, &strFormat, &brushShadow); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR(pGraphic) // DECL_REF_EXPR(pGraphic) // OVERLOADED_DECL_REF(DrawString) // DECL_REF_EXPR(strName) // UNARY_OPERATOR() // INTEGER_LITERAL() // UNARY_OPERATOR() // DECL_REF_EXPR(font) // DECL_REF_EXPR(ptString) // UNARY_OPERATOR() // DECL_REF_EXPR(strFormat) // UNARY_OPERATOR() // DECL_REF_EXPR(brushShadow)
	ptString.X = (Gdiplus::REAL)fTextGap; // BINARY_OPERATOR() // MEMBER_REF_EXPR(X) // DECL_REF_EXPR(ptString) // CSTYLE_CAST_EXPR() // NAMESPACE_REF(Gdiplus) // TYPE_REF(Gdiplus::REAL) // UNEXPOSED_EXPR(fTextGap) // DECL_REF_EXPR(fTextGap)
	ptString.Y = (Gdiplus::REAL)4; // BINARY_OPERATOR() // MEMBER_REF_EXPR(Y) // DECL_REF_EXPR(ptString) // CSTYLE_CAST_EXPR() // NAMESPACE_REF(Gdiplus) // TYPE_REF(Gdiplus::REAL) // UNEXPOSED_EXPR() // INTEGER_LITERAL()
	pGraphic->DrawString(strName, -1, &font, ptString, &strFormat, &brush); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR(pGraphic) // DECL_REF_EXPR(pGraphic) // OVERLOADED_DECL_REF(DrawString) // DECL_REF_EXPR(strName) // UNARY_OPERATOR() // INTEGER_LITERAL() // UNARY_OPERATOR() // DECL_REF_EXPR(font) // DECL_REF_EXPR(ptString) // UNARY_OPERATOR() // DECL_REF_EXPR(strFormat) // UNARY_OPERATOR() // DECL_REF_EXPR(brush)
}

void CActuatorPanoFixture::DrawLibModel(CImgBuf* pImgbuf) // CXX_METHOD(DrawLibModel) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(pImgbuf) // TYPE_REF(class CImgBuf)
{ // COMPOUND_STMT()
	auto pDSI = (CDSILibraryDrawer*)LookupDSI(DSI_NAME_PANO_IMP_LIB_DRAWER, 0); // DECL_STMT() // VAR_DECL(pDSI) // CSTYLE_CAST_EXPR() // TYPE_REF(class CDSILibraryDrawer) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(LookupDSI) // STRING_LITERAL(L"DSI_MODEL_DRAWER") // INTEGER_LITERAL()
	if (pDSI) // IF_STMT() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSI)
	{ // COMPOUND_STMT()
		auto start = std::chrono::steady_clock::now(); // DECL_STMT() // VAR_DECL(start) // CALL_EXPR() // UNEXPOSED_EXPR()

		pDSI->UpdateModel(); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(pDSI)
		auto vInfo = pDSI->getCamInfoForDraw(); // DECL_STMT() // VAR_DECL(vInfo) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR()
		int tempIdx = PATCHLINE_PREVIEW_SPHERE_INDEX; // DECL_STMT() // VAR_DECL(tempIdx) // UNEXPOSED_EXPR(PATCHLINE_PREVIEW_SPHERE_INDEX) // DECL_REF_EXPR(PATCHLINE_PREVIEW_SPHERE_INDEX)

		CPanoActImgInfo panoInfo; // DECL_STMT() // VAR_DECL(panoInfo) // TYPE_REF(class CPanoActImgInfo) // CALL_EXPR(CPanoActImgInfo)
		GetPanoActImgInfo(panoInfo); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetPanoActImgInfo) // DECL_REF_EXPR(panoInfo)

		auto vNormal = panoInfo.GetVNormalVectorPosMv(); // DECL_STMT() // VAR_DECL(vNormal) // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(panoInfo)
		if (vNormal.size()) // IF_STMT() // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(vNormal)
		{ // COMPOUND_STMT()
			//auto fNormal = vNormal[vNormal.size() / 2];
			//auto fUp = panoInfo.GetVScrVector()[0];
			//auto fCross = vTan[vTan.size() / 2];

			for (int i = 0; i < vInfo.size(); ++i) // FOR_STMT() // DECL_STMT() // VAR_DECL(i) // INTEGER_LITERAL() // CALL_EXPR() // DECL_REF_EXPR(i) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(vInfo) // UNARY_OPERATOR() // DECL_REF_EXPR(i)
			{ // COMPOUND_STMT()
				_pImgRenderer->RemoveAllMeshModel(); // CALL_EXPR(RemoveAllMeshModel) // MEMBER_REF_EXPR(RemoveAllMeshModel) // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer)
				if (_pImgRenderer->IsEmptyModelNumber(tempIdx)) // IF_STMT() // CALL_EXPR(IsEmptyModelNumber) // MEMBER_REF_EXPR(IsEmptyModelNumber) // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer) // UNEXPOSED_EXPR(tempIdx) // UNEXPOSED_EXPR(tempIdx) // DECL_REF_EXPR(tempIdx)
					_pImgRenderer->AddMeshModel(vInfo[i].pDocModel, tempIdx); // CALL_EXPR(AddMeshModel) // MEMBER_REF_EXPR(AddMeshModel) // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer) // MEMBER_REF_EXPR() // ARRAY_SUBSCRIPT_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(i) // DECL_REF_EXPR(tempIdx)
				_pImgRenderer->SetLightColor(vInfo[i].color, 1.f, tempIdx); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer) // OVERLOADED_DECL_REF(SetLightColor) // MEMBER_REF_EXPR() // ARRAY_SUBSCRIPT_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(i) // FLOATING_LITERAL() // DECL_REF_EXPR(tempIdx)
				_pImgRenderer->SetTransformedMatrix(&vInfo[i].mTrans, tempIdx++); // CALL_EXPR(SetTransformedMatrix) // MEMBER_REF_EXPR(SetTransformedMatrix) // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer) // CALL_EXPR() // MEMBER_REF_EXPR() // ARRAY_SUBSCRIPT_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(i) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator&) // UNARY_OPERATOR() // DECL_REF_EXPR(tempIdx)

				float3 fPos = vInfo[i].fPos; // DECL_STMT() // VAR_DECL(fPos) // TYPE_REF(struct DioData::float3) // MEMBER_REF_EXPR() // ARRAY_SUBSCRIPT_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(i)
				float3 fNormal = vInfo[i].fNormal; // DECL_STMT() // VAR_DECL(fNormal) // TYPE_REF(struct DioData::float3) // MEMBER_REF_EXPR() // ARRAY_SUBSCRIPT_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(i)
				float3 fUp = vInfo[i].fUp; // DECL_STMT() // VAR_DECL(fUp) // TYPE_REF(struct DioData::float3) // MEMBER_REF_EXPR() // ARRAY_SUBSCRIPT_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(i)
				//float sqrDis = vInfo[i].sqrDistance;
				//float3 shortestPt = vInfo[i].shortestPt;

				auto CP = vInfo[i].world2Point; // DECL_STMT() // VAR_DECL(CP) // MEMBER_REF_EXPR() // ARRAY_SUBSCRIPT_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(i)
				

				_pImgRenderer->SetScreenPos(CP); // CALL_EXPR(SetScreenPos) // MEMBER_REF_EXPR(SetScreenPos) // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer) // UNEXPOSED_EXPR()

				const CSize ImgSize(pImgbuf->Width(), pImgbuf->Height()); // DECL_STMT() // VAR_DECL(ImgSize) // TYPE_REF(class CSize) // CALL_EXPR(CSize) // CALL_EXPR(Width) // MEMBER_REF_EXPR(Width) // UNEXPOSED_EXPR(pImgbuf) // UNEXPOSED_EXPR(pImgbuf) // DECL_REF_EXPR(pImgbuf) // CALL_EXPR(Height) // MEMBER_REF_EXPR(Height) // UNEXPOSED_EXPR(pImgbuf) // UNEXPOSED_EXPR(pImgbuf) // DECL_REF_EXPR(pImgbuf)
				_pImgRenderer->DrawModelPanorama(fPos, fNormal, fUp, float3(1, 0, 0), m_fMilliMeterPerPixel, ImgSize); // UNEXPOSED_EXPR() // CALL_EXPR(DrawModelPanorama) // MEMBER_REF_EXPR(DrawModelPanorama) // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer) // UNEXPOSED_EXPR(fPos) // DECL_REF_EXPR(fPos) // UNEXPOSED_EXPR(fNormal) // DECL_REF_EXPR(fNormal) // UNEXPOSED_EXPR(fUp) // DECL_REF_EXPR(fUp) // UNEXPOSED_EXPR() // UNEXPOSED_EXPR(float3) // CALL_EXPR(float3) // TYPE_REF(struct DioData::float3) // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR() // INTEGER_LITERAL() // UNEXPOSED_EXPR(m_fMilliMeterPerPixel) // MEMBER_REF_EXPR(m_fMilliMeterPerPixel) // DECL_REF_EXPR(ImgSize)

			}

			_pImgRenderer->GetImage_PanoMesh(*pImgbuf); // CALL_EXPR(GetImage_PanoMesh) // MEMBER_REF_EXPR(GetImage_PanoMesh) // UNEXPOSED_EXPR(_pImgRenderer) // MEMBER_REF_EXPR(_pImgRenderer) // UNARY_OPERATOR() // UNEXPOSED_EXPR(pImgbuf) // DECL_REF_EXPR(pImgbuf)

			auto end = std::chrono::steady_clock::now(); // DECL_STMT() // VAR_DECL(end) // CALL_EXPR() // UNEXPOSED_EXPR()
			std::chrono::duration<double> totalTime = end - start; // DECL_STMT() // VAR_DECL(totalTime)
			cout << "PanoFixture Draw Lib total : " << totalTime.count() << endl; // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(cout) // STRING_LITERAL("PanoFixture Draw Lib total : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(endl)
		}
	}
}

void CActuatorPanoFixture::MakeImage(volatile bool* pbContinue /*= nullptr*/) // CXX_METHOD(MakeImage) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(pbContinue)
{ // COMPOUND_STMT()
	auto start = std::chrono::steady_clock::now(); // DECL_STMT() // VAR_DECL(start) // CALL_EXPR() // UNEXPOSED_EXPR()
	UNREFERENCED_PARAMETER(pbContinue); // PAREN_EXPR() // DECL_REF_EXPR(pbContinue)

	auto eType = GetLocalDocAP()->GetSelScanModelTy(); // DECL_STMT() // VAR_DECL(eType) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP)
	auto eStep = GetLocalDocAP()->GetCurrentStep(); // DECL_STMT() // VAR_DECL(eStep) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP)
	bool bNeedChange = true; // DECL_STMT() // VAR_DECL(bNeedChange) // CXX_BOOL_LITERAL_EXPR()

	auto panoInfo = GetLocalDocAP()->GetWritablePanoInfo(); // DECL_STMT() // VAR_DECL(panoInfo) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetLocalDocAP)

	panoInfo->GetNeedChngPano(eStep, eType, bNeedChange); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(panoInfo) // UNEXPOSED_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(bNeedChange)
	bNeedChange = _bNeedDrawCT || bNeedChange;	 // BINARY_OPERATOR() // DECL_REF_EXPR(bNeedChange) // BINARY_OPERATOR() // UNEXPOSED_EXPR(_bNeedDrawCT) // MEMBER_REF_EXPR(_bNeedDrawCT) // UNEXPOSED_EXPR(bNeedChange) // DECL_REF_EXPR(bNeedChange)

	//변화가 필요없고 재사용 가능하면 재사용
	if(NOT bNeedChange AND _pCTImgBuf.get()) // IF_STMT() // UNEXPOSED_EXPR()
	{ // COMPOUND_STMT()
		auto copy_start = std::chrono::high_resolution_clock::now(); // DECL_STMT() // VAR_DECL(copy_start) // CALL_EXPR() // UNEXPOSED_EXPR()

		CImgBuf& imgBuf = GetImageBuf(); // DECL_STMT() // VAR_DECL(imgBuf) // TYPE_REF(class CImgBuf) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetImageBuff) // DECL_STMT() // VAR_DECL(__doitUnqPtrForImgBuf__) // NULL_STMT()
		imgBuf.CopyFrom(*_pCTImgBuf.get());

		auto copy_end = std::chrono::high_resolution_clock::now(); // DECL_STMT() // VAR_DECL(copy_end) // CALL_EXPR() // UNEXPOSED_EXPR()
		auto copy_time = std::chrono::duration_cast<std::chrono::milliseconds>(copy_end - copy_start).count(); // DECL_STMT() // VAR_DECL(copy_time) // CALL_EXPR() // MEMBER_REF_EXPR() // CALL_EXPR() // DECL_REF_EXPR() // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // OVERLOADED_DECL_REF(duration_cast) // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // TYPE_REF(std::chrono::milliseconds) // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator-) // UNEXPOSED_EXPR()
	}
	else //그 외는 전부 갱신
	{ // COMPOUND_STMT()
		
		auto make_start = std::chrono::high_resolution_clock::now(); // DECL_STMT() // VAR_DECL(make_start) // CALL_EXPR() // UNEXPOSED_EXPR()
		__super::MakeImage(pbContinue); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(MakeImage) // DECL_REF_EXPR(pbContinue)
		auto make_end = std::chrono::high_resolution_clock::now(); // DECL_STMT() // VAR_DECL(make_end) // CALL_EXPR() // UNEXPOSED_EXPR()
		auto make_time = std::chrono::duration_cast<std::chrono::milliseconds>(make_end - make_start).count(); // DECL_STMT() // VAR_DECL(make_time) // CALL_EXPR() // MEMBER_REF_EXPR() // CALL_EXPR() // DECL_REF_EXPR() // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // OVERLOADED_DECL_REF(duration_cast) // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // TYPE_REF(std::chrono::milliseconds) // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator-) // UNEXPOSED_EXPR()

		panoInfo->SetNeedChngPano(eStep, eType, false); // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(panoInfo) // UNEXPOSED_EXPR() // UNEXPOSED_EXPR() // CXX_BOOL_LITERAL_EXPR()
	}
	//SR 그리기 태스트 #3959
	CImgBuf& imgBuf = GetImageBuf(); // DECL_STMT() // VAR_DECL(imgBuf) // TYPE_REF(class CImgBuf) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetImageBuff) // DECL_STMT() // VAR_DECL(__doitUnqPtrForImgBuf__) // NULL_STMT()

	//_pCTImgBuf = std::make_shared<CImgBuf>(imgBuf);
	DrawLibModel(&imgBuf); // CALL_EXPR(DrawLibModel) // MEMBER_REF_EXPR(DrawLibModel) // UNARY_OPERATOR() // DECL_REF_EXPR(imgBuf)

	auto end = std::chrono::steady_clock::now(); // DECL_STMT() // VAR_DECL(end) // CALL_EXPR() // UNEXPOSED_EXPR()
	std::chrono::duration<double> totalTime = end - start; // DECL_STMT() // VAR_DECL(totalTime)
	cout << "PanoFixture MakeImage total : " << totalTime.count() << endl; // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(cout) // STRING_LITERAL("PanoFixture MakeImage total : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CALL_EXPR() // MEMBER_REF_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(endl)
}

#include "../AppUICore/UIPane.h"
void CActuatorPanoFixture::UpdateActuator(bool bMakeImage) // CXX_METHOD(UpdateActuator) // TYPE_REF(class CActuatorPanoFixture) // PARM_DECL(bMakeImage)
{ // COMPOUND_STMT()
	__super::UpdateActuator(bMakeImage); // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(UpdateActuator) // DECL_REF_EXPR(bMakeImage)
}


#include "../DoitPrimitive/SurfaceModelitem.h"
#include "../AppUICore/UIPane.h"
//#define ALL_ADD
void CActuatorPanoFixture::TestDrawFixture() // CXX_METHOD(TestDrawFixture) // TYPE_REF(class CActuatorPanoFixture)
{ // COMPOUND_STMT()
	//PanoActImgInfo가 있을 경우
	CPanoActImgInfo panoImgInfo; // DECL_STMT() // VAR_DECL(panoImgInfo) // TYPE_REF(class CPanoActImgInfo) // CALL_EXPR(CPanoActImgInfo)
	auto start = std::chrono::high_resolution_clock::now(); // DECL_STMT() // VAR_DECL(start) // CALL_EXPR() // UNEXPOSED_EXPR()
	if (_pLocalDoc && GetPanoActImgInfo(panoImgInfo)) // IF_STMT() // BINARY_OPERATOR() // MEMBER_REF_EXPR(_pLocalDoc) // UNEXPOSED_EXPR() // MEMBER_REF_EXPR(GetPanoActImgInfo) // DECL_REF_EXPR(panoImgInfo)
	{ // COMPOUND_STMT()
		auto start = std::chrono::high_resolution_clock::now(); // DECL_STMT() // VAR_DECL(start) // CALL_EXPR() // UNEXPOSED_EXPR()
		int checkDecimal = 1000;	// // DECL_STMT() // VAR_DECL(checkDecimal) // INTEGER_LITERAL()

		std::vector<CPoint> vNervePanoPoint;	//결과 // DECL_STMT() // VAR_DECL(vNervePanoPoint)
		//이상하긴 하지만 key는 float의 int화 값 pair는 min, max의 인덱스 <key : floatX, value<MinIdx, MaxIdx >>
		std::map<int, std::pair<int, int>> xBaseMinMaxMap; // DECL_STMT() // VAR_DECL(xBaseMinMaxMap)

		auto pToothDoc = _pLocalDoc->GetToothDoc(); // DECL_STMT() // VAR_DECL(pToothDoc) // CALL_EXPR(GetToothDoc) // MEMBER_REF_EXPR(GetToothDoc) // UNEXPOSED_EXPR(_pLocalDoc) // MEMBER_REF_EXPR(_pLocalDoc)
		for (auto nTooth : pToothDoc->GetToothNumberList())
		{
			auto pToothData = _pToothInfoData->GetToothData(nTooth);
			auto fixtureName = pToothData->GetFixtureData()->GetName();
			auto pFixtureModel = _pLocalDoc->GetSurfaceModel(fixtureName);
			if (pFixtureModel == nullptr)
				continue;

			CSurfaceModelItem copyFixture = *pFixtureModel;
			copyFixture.UpdateDataWithTransMatrix(pToothData->GetFixtureData()->GetMatrix());
			auto pInfo =copyFixture.GetInfo();
			for (int i = 0; i < pInfo->nVertexCount; i++)
			{
				auto fPos = pInfo->pVertex[i].fPosition;
				int x2int = (checkDecimal * fPos.fValue[0] + 0.5); //첫째 자리만 , 2 이후 반올림 처리

				//빈경우 추가
				if (xBaseMinMaxMap.find(x2int) == xBaseMinMaxMap.end())
				{
					xBaseMinMaxMap[x2int] = std::pair<int, int>(i, i);
				}
				else
				{
					int minIdx = xBaseMinMaxMap[x2int].first;
					int maxIdx = xBaseMinMaxMap[x2int].second;

					if (fPos.fValue[1] < pInfo->pVertex[minIdx].fPosition[1])
						xBaseMinMaxMap[x2int] = std::pair<int, int>(i, maxIdx);
					else if (pInfo->pVertex[maxIdx].fPosition[1] < fPos.fValue[1])
						xBaseMinMaxMap[x2int] = std::pair<int, int>(minIdx, i);
				}

			}

			for (auto result : xBaseMinMaxMap)
			{
				vNervePanoPoint.push_back(World2PanoPoint(pInfo->pVertex[result.second.first].fPosition));
				if (result.second.first != result.second.second)
					vNervePanoPoint.push_back(World2PanoPoint(pInfo->pVertex[result.second.second].fPosition));
			}


		}
		
		auto end = std::chrono::high_resolution_clock::now(); // DECL_STMT() // VAR_DECL(end) // CALL_EXPR() // UNEXPOSED_EXPR()
		auto callPassMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count(); // DECL_STMT() // VAR_DECL(callPassMs) // CALL_EXPR() // MEMBER_REF_EXPR() // CALL_EXPR() // DECL_REF_EXPR() // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // OVERLOADED_DECL_REF(duration_cast) // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // TYPE_REF(std::chrono::milliseconds) // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator-) // UNEXPOSED_EXPR()
		std::cout << "Call Pass : " << callPassMs << " ms " << std::endl; // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(cout) // NAMESPACE_REF(std) // STRING_LITERAL("Call Pass : ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" ms ") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // DECL_REF_EXPR() // NAMESPACE_REF(std) // OVERLOADED_DECL_REF(endl)

		
		auto pDC = m_pParentPane->GetDC(); // DECL_STMT() // VAR_DECL(pDC) // CALL_EXPR(GetDC) // MEMBER_REF_EXPR(GetDC) // UNEXPOSED_EXPR(m_pParentPane) // UNEXPOSED_EXPR(m_pParentPane) // MEMBER_REF_EXPR(m_pParentPane)
		for (auto point : vNervePanoPoint)
			pDC->SetPixel(point, RGB(113, 120, 135));
		m_pParentPane->ReleaseDC(pDC); // CALL_EXPR(ReleaseDC) // MEMBER_REF_EXPR(ReleaseDC) // UNEXPOSED_EXPR(m_pParentPane) // UNEXPOSED_EXPR(m_pParentPane) // MEMBER_REF_EXPR(m_pParentPane) // UNEXPOSED_EXPR(pDC) // DECL_REF_EXPR(pDC)
		end = std::chrono::high_resolution_clock::now(); // BINARY_OPERATOR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(end) // CALL_EXPR() // UNEXPOSED_EXPR()
		auto printPassMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count(); // DECL_STMT() // VAR_DECL(printPassMs) // CALL_EXPR() // MEMBER_REF_EXPR() // CALL_EXPR() // DECL_REF_EXPR() // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // OVERLOADED_DECL_REF(duration_cast) // NAMESPACE_REF(std) // NAMESPACE_REF(chrono) // TYPE_REF(std::chrono::milliseconds) // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator-) // UNEXPOSED_EXPR()
		std::cout << printPassMs << " ms" << std::endl; // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // DECL_REF_EXPR(cout) // NAMESPACE_REF(std) // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" ms") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // DECL_REF_EXPR() // NAMESPACE_REF(std) // OVERLOADED_DECL_REF(endl)

		std::cout << "total" << callPassMs + printPassMs << " ms" << std::endl; // CALL_EXPR() // CALL_EXPR() // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR(cout) // NAMESPACE_REF(std) // STRING_LITERAL("total") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // CALL_EXPR() // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator+) // UNEXPOSED_EXPR() // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // STRING_LITERAL(" ms") // DECL_REF_EXPR() // OVERLOADED_DECL_REF(operator<<) // DECL_REF_EXPR() // NAMESPACE_REF(std) // OVERLOADED_DECL_REF(endl)
	}
} // UNEXPOSED_EXPR() // UNEXPOSED_EXPR() // UNEXPOSED_EXPR() // UNEXPOSED_EXPR() // UNEXPOSED_EXPR()