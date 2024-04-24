void OnInitialUpdate(void)
{
	__super::OnInitialUpdate();

	CRect rcClient;
	GetClientRect(rcClient);

	// step에 맞는 화면 구성을 위해 호출
	ResizeInternal(rcClient);
}
