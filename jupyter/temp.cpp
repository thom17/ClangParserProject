void OnInitialUpdate(void)
{
	__super::OnInitialUpdate();

	CRect rcClient;
	GetClientRect(rcClient);

	// step�� �´� ȭ�� ������ ���� ȣ��
	ResizeInternal(rcClient);
}
