"""
Make sure the UI widgets are configured correctly and work as expected.
"""
from PyQt5.QtWidgets import QWidget, QApplication, QWidgetItem, QSpacerItem, QVBoxLayout, \
    QMessageBox
from tests import factory
from securedrop_client import db
from securedrop_client import logic
from securedrop_client.gui.widgets import ToolBar, MainView, SourceList, SourceWidget, \
    LoginDialog, SpeechBubble, ConversationWidget, MessageWidget, ReplyWidget, FileWidget, \
    ConversationView, DeleteSourceMessageBox, DeleteSourceAction, SourceMenu


app = QApplication([])


def test_ToolBar_init():
    """
    Ensure the ToolBar instance is correctly set up.
    """
    tb = ToolBar(None)
    assert "Signed out." in tb.user_state.text()


def test_ToolBar_setup(mocker):
    """
    Calling setup with references to a window and controller object results in
    them becoming attributes of self.
    """
    tb = ToolBar(None)

    mock_window = mocker.MagicMock()
    mock_controller = mocker.MagicMock()

    tb.setup(mock_window, mock_controller)

    assert tb.window == mock_window
    assert tb.controller == mock_controller


def test_ToolBar_set_logged_in_as(mocker):
    """Given a username, the user_state is updated and login/logout
    buttons, and refresh buttons, are in the correct state.
    """
    tb = ToolBar(None)

    tb.user_state = mocker.MagicMock()
    tb.login = mocker.MagicMock()
    tb.logout = mocker.MagicMock()
    tb.refresh = mocker.MagicMock()

    tb.set_logged_in_as('test')

    tb.user_state.setText.assert_called_once_with('Signed in as: test')
    tb.login.setVisible.assert_called_once_with(False)
    tb.logout.setVisible.assert_called_once_with(True)
    tb.refresh.setVisible.assert_called_once_with(True)


def test_ToolBar_set_logged_out(mocker):
    """
    Ensure the UI reverts to the logged out state.
    """
    tb = ToolBar(None)

    tb.user_state = mocker.MagicMock()
    tb.login = mocker.MagicMock()
    tb.logout = mocker.MagicMock()
    tb.refresh = mocker.MagicMock()

    tb.set_logged_out()

    tb.user_state.setText.assert_called_once_with('Signed out.')
    tb.login.setVisible.assert_called_once_with(True)
    tb.logout.setVisible.assert_called_once_with(False)
    tb.refresh.setVisible.assert_called_once_with(False)


def test_ToolBar_on_login_clicked(mocker):
    """
    When login button is clicked, the window activates the login form.
    """
    tb = ToolBar(None)
    tb.window = mocker.MagicMock()
    tb.on_login_clicked()
    tb.window.show_login.assert_called_once_with()


def test_ToolBar_on_logout_clicked(mocker):
    """
    When logout is clicked, the logout logic from the controller is started.
    """
    tb = ToolBar(None)
    tb.controller = mocker.MagicMock()
    tb.on_logout_clicked()
    tb.controller.logout.assert_called_once_with()


def test_ToolBar_on_refresh_clicked(mocker):
    """
    When refresh is clicked, the refresh logic from the controller is stated.
    """
    tb = ToolBar(None)
    tb.controller = mocker.MagicMock()
    tb.on_refresh_clicked()
    tb.controller.sync_api.assert_called_once_with()


def test_ToolBar_sync_event():
    """Toggles refresh button when syncing
    """
    tb = ToolBar(None)
    tb._on_sync_event('syncing')
    assert not tb.refresh.isEnabled()

    tb._on_sync_event('synced')
    assert tb.refresh.isEnabled()


def test_MainView_init():
    """
    Ensure the MainView instance is correctly set up.
    """
    mv = MainView(None)
    assert isinstance(mv.source_list, SourceList)
    assert isinstance(mv.view_holder, QWidget)


def test_MainView_show_conversation(mocker):
    """
    Ensure the passed-in widget is added to the layout of the main view holder
    (i.e. that area of the screen on the right hand side).
    """
    mv = MainView(None)
    mv.view_layout = mocker.MagicMock()

    mock_widget = mocker.MagicMock()
    mv.set_conversation(mock_widget)

    mv.view_layout.takeAt.assert_called_once_with(0)
    mv.view_layout.addWidget.assert_called_once_with(mock_widget)


def test_MainView_update_error_status(mocker):
    """
    Ensure when the update_error_status method is called on the MainView that
    the error status text is set as expected.
    """
    mv = MainView(None)
    expected_message = "this is the message to be displayed"

    mv.error_status = mocker.MagicMock()
    mv.error_status.setText = mocker.MagicMock()

    mv.update_error_status(error=expected_message)
    mv.error_status.setText.assert_called_once_with(expected_message)


def test_SourceList_update(mocker):
    """
    Check the items in the source list are cleared and a new SourceWidget for
    each passed-in source is created along with an associated QListWidgetItem.
    """
    sl = SourceList(None)

    sl.clear = mocker.MagicMock()
    sl.addItem = mocker.MagicMock()
    sl.setItemWidget = mocker.MagicMock()
    sl.controller = mocker.MagicMock()

    mock_sw = mocker.MagicMock()
    mock_lwi = mocker.MagicMock()
    mocker.patch('securedrop_client.gui.widgets.SourceWidget', mock_sw)
    mocker.patch('securedrop_client.gui.widgets.QListWidgetItem', mock_lwi)

    sources = ['a', 'b', 'c', ]
    sl.update(sources)

    sl.clear.assert_called_once_with()
    assert mock_sw.call_count == len(sources)
    assert mock_lwi.call_count == len(sources)
    assert sl.addItem.call_count == len(sources)
    assert sl.setItemWidget.call_count == len(sources)


def test_SourceList_maintains_selection(mocker):
    """
    Maintains the selected item if present in new list
    """
    sl = SourceList(None)
    sources = [factory.Source(), factory.Source()]
    sl.setup(mocker.MagicMock())
    sl.update(sources)

    sl.setCurrentItem(sl.itemAt(0, 0))
    sl.update(sources)

    assert sl.currentItem()
    assert sl.itemWidget(sl.currentItem()).source.id == sources[0].id


def test_SourceWidget_init(mocker):
    """
    The source widget is initialised with the passed-in source.
    """
    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo bar baz'
    sw = SourceWidget(None, mock_source)
    assert sw.source == mock_source


def test_SourceWidget_setup(mocker):
    """
    The setup method adds the controller as an attribute on the SourceWidget.
    """
    mock_controller = mocker.MagicMock()
    mock_source = mocker.MagicMock()

    sw = SourceWidget(None, mock_source)
    sw.setup(mock_controller)

    assert sw.controller == mock_controller


def test_SourceWidget_html_init(mocker):
    """
    The source widget is initialised with the given source name, with
    HTML escaped properly.
    """
    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo <b>bar</b> baz'

    sw = SourceWidget(None, mock_source)
    sw.name = mocker.MagicMock()
    sw.summary_layout = mocker.MagicMock()

    mocker.patch('securedrop_client.gui.widgets.load_svg')
    sw.update()

    sw.name.setText.assert_called_once_with('<strong>foo &lt;b&gt;bar&lt;/b&gt; baz</strong>')


def test_SourceWidget_update_starred(mocker):
    """
    Ensure the widget displays the expected details from the source.
    """
    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo bar baz'
    mock_source.is_starred = True

    sw = SourceWidget(None, mock_source)
    sw.name = mocker.MagicMock()
    sw.summary_layout = mocker.MagicMock()

    mock_load = mocker.patch('securedrop_client.gui.widgets.load_svg')
    sw.update()

    mock_load.assert_called_once_with('star_on.svg')
    sw.name.setText.assert_called_once_with('<strong>foo bar baz</strong>')


def test_SourceWidget_update_unstarred(mocker):
    """
    Ensure the widget displays the expected details from the source.
    """
    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo bar baz'
    mock_source.is_starred = False

    sw = SourceWidget(None, mock_source)
    sw.name = mocker.MagicMock()
    sw.summary_layout = mocker.MagicMock()

    mock_load = mocker.patch('securedrop_client.gui.widgets.load_svg')
    sw.update()

    mock_load.assert_called_once_with('star_off.svg')
    sw.name.setText.assert_called_once_with('<strong>foo bar baz</strong>')


def test_SourceWidget_update_attachment_icon():
    """
    Attachment icon identicates document count
    """
    source = factory.Source(document_count=1)
    sw = SourceWidget(None, source)

    sw.update()
    assert not sw.attached.isHidden()

    source.document_count = 0

    sw.update()
    assert sw.attached.isHidden()


def test_SourceWidget_toggle_star(mocker):
    """
    The toggle_star method should call self.controller.update_star
    """
    mock_controller = mocker.MagicMock()
    mock_source = mocker.MagicMock()
    event = mocker.MagicMock()

    sw = SourceWidget(None, mock_source)
    sw.controller = mock_controller
    sw.controller.update_star = mocker.MagicMock()

    sw.toggle_star(event)
    sw.controller.update_star.assert_called_once_with(mock_source)


def test_SourceWidget_delete_source(mocker):
    mock_source = mocker.MagicMock()
    mock_delete_source_message_box_object = mocker.MagicMock(DeleteSourceMessageBox)
    mock_controller = mocker.MagicMock()
    mock_delete_source_message = mocker.MagicMock(
        return_value=mock_delete_source_message_box_object)

    sw = SourceWidget(None, mock_source)
    sw.controller = mock_controller

    mocker.patch(
        "securedrop_client.gui.widgets.DeleteSourceMessageBox",
        mock_delete_source_message,
    )

    sw.delete_source(None)
    mock_delete_source_message_box_object.launch.assert_called_with()


def test_SourceWidget_delete_source_when_user_chooses_cancel(mocker):
    mock_message_box_question = mocker.MagicMock(QMessageBox.question)
    mock_message_box_question.return_value = QMessageBox.Cancel

    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo bar baz'
    mock_source.submissions = []

    submission_files = (
        "submission_1-msg.gpg",
        "submission_2-msg.gpg",
        "submission_3-doc.gpg",
    )
    for filename in submission_files:
        submission = mocker.MagicMock()
        submission.filename = filename
        mock_source.submissions.append(submission)

    mock_controller = mocker.MagicMock()
    sw = SourceWidget(None, mock_source)
    sw.controller = mock_controller

    mocker.patch(
        "securedrop_client.gui.widgets.QMessageBox.question",
        mock_message_box_question,
    )
    sw.delete_source(None)
    sw.controller.delete_source.assert_not_called()


def test_LoginDialog_setup(mocker):
    """
    The LoginView is correctly initialised.
    """
    mock_controller = mocker.MagicMock()
    ld = LoginDialog(None)
    ld.setup(mock_controller)
    assert ld.controller == mock_controller
    assert ld.title.text() == '<h1>Sign in</h1>'


def test_LoginDialog_reset(mocker):
    """
    Ensure the state of the login view is returned to the correct state.
    """
    mock_controller = mocker.MagicMock()

    ld = LoginDialog(None)
    ld.setup(mock_controller)
    ld.username_field = mocker.MagicMock()
    ld.password_field = mocker.MagicMock()
    ld.tfa_field = mocker.MagicMock()
    ld.setDisabled = mocker.MagicMock()
    ld.error_label = mocker.MagicMock()

    ld.reset()

    ld.username_field.setText.assert_called_once_with('')
    ld.password_field.setText.assert_called_once_with('')
    ld.tfa_field.setText.assert_called_once_with('')
    ld.setDisabled.assert_called_once_with(False)
    ld.error_label.setText.assert_called_once_with('')


def test_LoginDialog_error(mocker):
    """
    Any error message passed in is assigned as the text for the error label.
    """
    mock_controller = mocker.MagicMock()
    ld = LoginDialog(None)
    ld.setup(mock_controller)
    ld.error_label = mocker.MagicMock()
    ld.error('foo')
    ld.error_label.setText.assert_called_once_with('foo')


def test_LoginDialog_validate_no_input(mocker):
    """
    If the user doesn't provide input, tell them and give guidance.
    """
    mock_controller = mocker.MagicMock()

    ld = LoginDialog(None)
    ld.setup(mock_controller)
    ld.username_field.text = mocker.MagicMock(return_value='')
    ld.password_field.text = mocker.MagicMock(return_value='')
    ld.tfa_field.text = mocker.MagicMock(return_value='')
    ld.setDisabled = mocker.MagicMock()
    ld.error = mocker.MagicMock()

    ld.validate()

    assert ld.setDisabled.call_count == 2
    assert ld.error.call_count == 1


def test_LoginDialog_validate_input_non_numeric_2fa(mocker):
    """
    If the user doesn't provide numeric 2fa input, tell them and give
    guidance.
    """
    mock_controller = mocker.MagicMock()

    ld = LoginDialog(None)
    ld.setup(mock_controller)
    ld.username_field.text = mocker.MagicMock(return_value='foo')
    ld.password_field.text = mocker.MagicMock(return_value='nicelongpassword')
    ld.tfa_field.text = mocker.MagicMock(return_value='baz')
    ld.setDisabled = mocker.MagicMock()
    ld.error = mocker.MagicMock()

    ld.validate()

    assert ld.setDisabled.call_count == 2
    assert ld.error.call_count == 1
    assert mock_controller.login.call_count == 0


def test_LoginDialog_validate_too_short_username(mocker):
    """
    If the username is too small, we show an informative error message.
    """
    mock_controller = mocker.MagicMock()

    ld = LoginDialog(None)
    ld.setup(mock_controller)
    ld.username_field.text = mocker.MagicMock(return_value='he')
    ld.password_field.text = mocker.MagicMock(return_value='nicelongpassword')
    ld.tfa_field.text = mocker.MagicMock(return_value='123456')
    ld.setDisabled = mocker.MagicMock()
    ld.error = mocker.MagicMock()

    ld.validate()

    assert ld.setDisabled.call_count == 2
    assert ld.error.call_count == 1
    assert mock_controller.login.call_count == 0


def test_LoginDialog_validate_too_short_password(mocker):
    """
    If the password is too small, we show an informative error message.
    """
    mock_controller = mocker.MagicMock()

    ld = LoginDialog(None)
    ld.setup(mock_controller)
    ld.username_field.text = mocker.MagicMock(return_value='foo')
    ld.password_field.text = mocker.MagicMock(return_value='bar')
    ld.tfa_field.text = mocker.MagicMock(return_value='123456')
    ld.setDisabled = mocker.MagicMock()
    ld.error = mocker.MagicMock()

    ld.validate()

    assert ld.setDisabled.call_count == 2
    assert ld.error.call_count == 1
    assert mock_controller.login.call_count == 0


def test_LoginDialog_validate_too_long_password(mocker):
    """
    If the password is too long, we show an informative error message.
    """
    mock_controller = mocker.MagicMock()
    ld = LoginDialog(None)
    ld.setup(mock_controller)

    max_password_len = 128
    too_long_password = 'a' * (max_password_len + 1)

    ld.username_field.text = mocker.MagicMock(return_value='foo')
    ld.password_field.text = mocker.MagicMock(return_value=too_long_password)
    ld.tfa_field.text = mocker.MagicMock(return_value='123456')
    ld.setDisabled = mocker.MagicMock()
    ld.error = mocker.MagicMock()

    ld.validate()

    assert ld.setDisabled.call_count == 2
    assert ld.error.call_count == 1
    assert mock_controller.login.call_count == 0


def test_LoginDialog_validate_input_ok(mocker):
    """
    Valid input from the user causes a call to the controller's login method.
    """
    mock_controller = mocker.MagicMock()

    ld = LoginDialog(None)
    ld.setup(mock_controller)
    ld.username_field.text = mocker.MagicMock(return_value='foo')
    ld.password_field.text = mocker.MagicMock(return_value='nicelongpassword')
    ld.tfa_field.text = mocker.MagicMock(return_value='123456')
    ld.setDisabled = mocker.MagicMock()
    ld.error = mocker.MagicMock()

    ld.validate()

    assert ld.setDisabled.call_count == 1
    assert ld.error.call_count == 0
    mock_controller.login.assert_called_once_with('foo', 'nicelongpassword', '123456')


def test_SpeechBubble_init(mocker):
    """
    Check the speech bubble is configured correctly (there's a label containing
    the passed in text).
    """
    mock_label = mocker.patch('securedrop_client.gui.widgets.QLabel')
    mocker.patch('securedrop_client.gui.widgets.QVBoxLayout')
    mocker.patch('securedrop_client.gui.widgets.SpeechBubble.setLayout')
    mock_signal = mocker.Mock()
    mock_connect = mocker.Mock()
    mock_signal.connect = mock_connect

    SpeechBubble('mock id', 'hello', mock_signal)
    mock_label.assert_called_once_with('hello')
    assert mock_connect.called


def test_SpeechBubble_update_text(mocker):
    """
    Check that the calling the slot updates the text.
    """
    mocker.patch('securedrop_client.gui.widgets.QVBoxLayout')
    mocker.patch('securedrop_client.gui.widgets.SpeechBubble.setLayout')
    mock_signal = mocker.MagicMock()

    msg_id = 'abc123'
    sb = SpeechBubble(msg_id, 'hello', mock_signal)

    new_msg = 'new message'
    sb._update_text(msg_id, new_msg)
    assert sb.message.text() == new_msg

    newer_msg = 'an even newer message'
    sb._update_text(msg_id + 'xxxxx', newer_msg)
    assert sb.message.text() == new_msg


def test_SpeechBubble_html_init(mocker):
    """
    Check the speech bubble is configured correctly (there's a label containing
    the passed in text, with HTML escaped properly).
    """
    mock_label = mocker.patch('securedrop_client.gui.widgets.QLabel')
    mocker.patch('securedrop_client.gui.widgets.QVBoxLayout')
    mocker.patch('securedrop_client.gui.widgets.SpeechBubble.setLayout')
    mock_signal = mocker.MagicMock()

    SpeechBubble('mock id', '<b>hello</b>', mock_signal)
    mock_label.assert_called_once_with('&lt;b&gt;hello&lt;/b&gt;')


def test_SpeechBubble_with_apostrophe_in_text(mocker):
    """Check Speech Bubble is displaying text with apostrophe correctly."""
    mock_label = mocker.patch('securedrop_client.gui.widgets.QLabel')
    mocker.patch('securedrop_client.gui.widgets.QVBoxLayout')
    mocker.patch('securedrop_client.gui.widgets.SpeechBubble.setLayout')
    mock_signal = mocker.MagicMock()

    message = "I'm sure, you are reading my message."
    SpeechBubble('mock id', message, mock_signal)
    mock_label.assert_called_once_with(message)


def test_ConversationWidget_init_left(mocker):
    """
    Check the ConversationWidget is configured correctly for align-left.
    """
    mock_signal = mocker.Mock()
    mock_connect = mocker.Mock()
    mock_signal.connect = mock_connect

    cw = ConversationWidget('mock id', 'hello', mock_signal, align='left')
    layout = cw.layout()

    assert isinstance(layout.takeAt(0), QWidgetItem)
    assert isinstance(layout.takeAt(0), QSpacerItem)
    assert mock_connect.called


def test_ConversationWidget_init_right(mocker):
    """
    Check the ConversationWidget is configured correctly for align-left.
    """
    mock_signal = mocker.Mock()
    mock_connect = mocker.Mock()
    mock_signal.connect = mock_connect

    cw = ConversationWidget('mock id', 'hello', mock_signal, align='right')
    layout = cw.layout()

    assert isinstance(layout.takeAt(0), QSpacerItem)
    assert isinstance(layout.takeAt(0), QWidgetItem)
    assert mock_connect.called


def test_MessageWidget_init(mocker):
    """
    Check the CSS is set as expected.
    """
    mock_signal = mocker.Mock()
    mock_connected = mocker.Mock()
    mock_signal.connect = mock_connected

    mw = MessageWidget('mock id', 'hello', mock_signal)
    ss = mw.styleSheet()

    assert 'background-color' in ss
    assert mock_connected.called


def test_ReplyWidget_init(mocker):
    """
    Check the CSS is set as expected.
    """
    mock_signal = mocker.Mock()
    mock_connected = mocker.Mock()
    mock_signal.connect = mock_connected

    rw = ReplyWidget('mock id', 'hello', mock_signal)
    ss = rw.styleSheet()

    assert 'background-color' in ss
    assert mock_connected.called


def test_FileWidget_init_left(mocker):
    """
    Check the FileWidget is configured correctly for align-left.
    """
    mock_controller = mocker.MagicMock()
    source = factory.Source()
    submission = db.Submission(source, 'submission-uuid', 123,
                               'mah-reply.gpg',
                               'http://mah-server/mah-reply-url')
    submission.is_downloaded = True

    fw = FileWidget(source, submission, mock_controller, align='left')

    layout = fw.layout()
    assert isinstance(layout.takeAt(0), QWidgetItem)
    assert isinstance(layout.takeAt(0), QWidgetItem)
    assert isinstance(layout.takeAt(0), QSpacerItem)
    assert fw.controller == mock_controller


def test_FileWidget_init_right(mocker):
    """
    Check the FileWidget is configured correctly for align-right.
    """
    mock_controller = mocker.MagicMock()
    source = factory.Source()
    submission = db.Submission(source, 'submission-uuid', 123,
                               'mah-reply.gpg',
                               'http://mah-server/mah-reply-url')
    submission.is_downloaded = True

    fw = FileWidget(source, submission, mock_controller, align='right')
    layout = fw.layout()
    assert isinstance(layout.takeAt(0), QSpacerItem)
    assert isinstance(layout.takeAt(0), QWidgetItem)
    assert isinstance(layout.takeAt(0), QWidgetItem)
    assert fw.controller == mock_controller


def test_FileWidget_mousePressEvent_download(mocker):
    """
    Should fire the expected download event handler in the logic layer.
    """
    mock_controller = mocker.MagicMock()
    source = factory.Source()
    submission = db.Submission(source, 'submission-uuid', 123,
                               'mah-reply.gpg',
                               'http://mah-server/mah-reply-url')
    submission.is_downloaded = False

    fw = FileWidget(source, submission, mock_controller)
    fw.mouseReleaseEvent(None)
    fw.controller.on_file_download.assert_called_once_with(source, submission)


def test_FileWidget_mousePressEvent_open(mocker):
    """
    Should fire the expected open event handler in the logic layer.
    """
    mock_controller = mocker.MagicMock()
    source = factory.Source()
    submission = db.Submission(source, 'submission-uuid', 123,
                               'mah-reply.gpg',
                               'http://mah-server/mah-reply-url')
    submission.is_downloaded = True

    fw = FileWidget(source, submission, mock_controller)
    fw.mouseReleaseEvent(None)
    fw.controller.on_file_open.assert_called_once_with(submission)


def test_ConversationView_init(mocker, homedir):
    """
    Ensure the conversation view has a layout to add widgets to.
    """
    mocked_source = mocker.MagicMock()
    mocked_controller = mocker.MagicMock()
    cv = ConversationView(mocked_source, homedir, mocked_controller)
    assert isinstance(cv.conversation_layout, QVBoxLayout)


def test_ConversationView_move_to_bottom(mocker, homedir):
    """
    Check the signal handler sets the correct value for the scrollbar to be
    the maximum possible value.
    """
    mocked_source = mocker.MagicMock()
    mocked_controller = mocker.MagicMock()

    cv = ConversationView(mocked_source, homedir, mocked_controller)

    cv.scroll = mocker.MagicMock()
    cv.move_to_bottom(0, 6789)
    cv.scroll.verticalScrollBar().setValue.assert_called_once_with(6789)


def test_ConversationView_add_message(mocker, homedir):
    """
    Adding a message results in a new MessageWidget added to the layout.
    """
    mocked_source = mocker.MagicMock()
    mocked_controller = mocker.MagicMock()

    cv = ConversationView(mocked_source, homedir, mocked_controller)
    cv.conversation_layout = mocker.MagicMock()

    cv.add_message('mock id', 'hello')
    assert cv.conversation_layout.addWidget.call_count == 1

    cal = cv.conversation_layout.addWidget.call_args_list
    assert isinstance(cal[0][0][0], MessageWidget)


def test_ConversationView_add_reply(mocker, homedir):
    """
    Adding a reply results in a new ReplyWidget added to the layout.
    """
    mocked_source = mocker.MagicMock()
    mocked_controller = mocker.MagicMock()

    cv = ConversationView(mocked_source, homedir, mocked_controller)
    cv.conversation_layout = mocker.MagicMock()

    cv.add_reply('mock id', 'hello')
    assert cv.conversation_layout.addWidget.call_count == 1

    cal = cv.conversation_layout.addWidget.call_args_list
    assert isinstance(cal[0][0][0], ReplyWidget)


def test_ConversationView_add_downloaded_file(mocker, homedir):
    """
    Adding a file results in a new FileWidget added to the layout with the
    proper QLabel.
    """
    mocked_source = mocker.MagicMock()
    mocked_controller = mocker.MagicMock()

    cv = ConversationView(mocked_source, homedir, mocked_controller)
    cv.conversation_layout = mocker.MagicMock()

    mock_source = mocker.MagicMock()
    mock_file = mocker.MagicMock()
    mock_file.is_downloaded = True
    mock_label = mocker.patch('securedrop_client.gui.widgets.QLabel')
    mocker.patch('securedrop_client.gui.widgets.QHBoxLayout.addWidget')
    mocker.patch('securedrop_client.gui.widgets.FileWidget.setLayout')

    cv.add_file(mock_source, mock_file)
    mock_label.assert_called_with("Open")
    assert cv.conversation_layout.addWidget.call_count == 1

    cal = cv.conversation_layout.addWidget.call_args_list
    assert isinstance(cal[0][0][0], FileWidget)


def test_ConversationView_add_not_downloaded_file(mocker, homedir):
    """
    Adding a file results in a new FileWidget added to the layout with the
    proper QLabel.
    """
    mocked_source = mocker.MagicMock()
    mocked_controller = mocker.MagicMock()

    cv = ConversationView(mocked_source, homedir, mocked_controller)
    cv.conversation_layout = mocker.MagicMock()

    mock_source = mocker.MagicMock()
    mock_file = mocker.MagicMock()
    mock_file.is_downloaded = False
    mock_file.size = 123
    mock_label = mocker.patch('securedrop_client.gui.widgets.QLabel')
    mocker.patch('securedrop_client.gui.widgets.QHBoxLayout.addWidget')
    mocker.patch('securedrop_client.gui.widgets.FileWidget.setLayout')

    cv.add_file(mock_source, mock_file)
    mock_label.assert_called_with("Download (123 bytes)")
    assert cv.conversation_layout.addWidget.call_count == 1

    cal = cv.conversation_layout.addWidget.call_args_list
    assert isinstance(cal[0][0][0], FileWidget)


def test_DeleteSourceMessageBox_init(mocker):
    mock_controller = mocker.MagicMock()
    mock_source = mocker.MagicMock()
    DeleteSourceMessageBox(None, mock_source, mock_controller)


def test_DeleteSourceMessage_launch_when_user_chooses_cancel(mocker):
    mock_message_box_question = mocker.MagicMock(QMessageBox.question)
    mock_message_box_question.return_value = QMessageBox.Cancel
    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo bar baz'
    mock_source.submissions = []

    submission_files = (
        "submission_1-msg.gpg",
        "submission_2-msg.gpg",
        "submission_3-doc.gpg",
    )
    for filename in submission_files:
        submission = mocker.MagicMock()
        submission.filename = filename
        mock_source.submissions.append(submission)

    mock_controller = mocker.MagicMock()
    delete_source_message_box = DeleteSourceMessageBox(
        None, mock_source, mock_controller
    )
    mocker.patch(
        "securedrop_client.gui.widgets.QMessageBox.question",
        mock_message_box_question,
    )

    delete_source_message_box.launch()
    mock_controller.delete_source.assert_not_called()


def test_DeleteSourceMssageBox_launch_when_user_chooses_yes(mocker):
    mock_message_box_question = mocker.MagicMock(QMessageBox.question)
    mock_message_box_question.return_value = QMessageBox.Yes
    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo bar baz'
    mock_source.submissions = []

    submission_files = (
        "submission_1-msg.gpg",
        "submission_2-msg.gpg",
        "submission_3-doc.gpg",
    )
    for filename in submission_files:
        submission = mocker.MagicMock()
        submission.filename = filename
        mock_source.submissions.append(submission)

    mock_controller = mocker.MagicMock()
    delete_source_message_box = DeleteSourceMessageBox(
        None, mock_source, mock_controller
    )
    mocker.patch(
        "securedrop_client.gui.widgets.QMessageBox.question",
        mock_message_box_question,
    )

    delete_source_message_box.launch()
    mock_controller.delete_source.assert_called_once_with(mock_source)

    message = (
        "<big>Deleting the Source account for "
        "<b>foo bar baz</b> will also "
        "delete 1 files and 2 messages.</big> "
        "<br> "
        "<small>This Source will no longer be able to correspond "
        "through the log-in tied to this account.</small>"
    )
    mock_message_box_question.assert_called_once_with(
        None,
        "",
        message,
        QMessageBox.Cancel | QMessageBox.Yes,
        QMessageBox.Cancel
    )


def test_DeleteSourceMessageBox_construct_message(mocker):
    mock_controller = mocker.MagicMock()
    mock_source = mocker.MagicMock()
    mock_source.journalist_designation = 'foo bar baz'
    mock_source.submissions = []

    submission_files = (
        "submission_1-msg.gpg",
        "submission_2-msg.gpg",
        "submission_3-doc.gpg",
    )
    for filename in submission_files:
        submission = mocker.MagicMock()
        submission.filename = filename
        mock_source.submissions.append(submission)

    delete_source_message_box = DeleteSourceMessageBox(
        None, mock_source, mock_controller
    )
    message = delete_source_message_box._construct_message(mock_source)

    expected_message = (
        "<big>Deleting the Source account for "
        "<b>foo bar baz</b> will also "
        "delete {files} files and {messages} messages.</big> "
        "<br> "
        "<small>This Source will no longer be able to correspond "
        "through the log-in tied to this account.</small>"
    ).format(files=1, messages=2)
    assert message == expected_message


def test_DeleteSourceAction_init(mocker):
    mock_controller = mocker.MagicMock()
    mock_source = mocker.MagicMock()
    DeleteSourceAction(
        mock_source,
        None,
        mock_controller
    )


def test_DeleteSourceAction_trigger(mocker):
    mock_controller = mocker.MagicMock()
    mock_source = mocker.MagicMock()
    mock_delete_source_message_box_obj = mocker.MagicMock()
    mock_delete_source_message_box = mocker.MagicMock()
    mock_delete_source_message_box.return_value = (
        mock_delete_source_message_box_obj
    )

    with mocker.patch(
        'securedrop_client.gui.widgets.DeleteSourceMessageBox',
        mock_delete_source_message_box
    ):
        delete_source_action = DeleteSourceAction(
            mock_source,
            None,
            mock_controller
        )
        delete_source_action.trigger()
        mock_delete_source_message_box_obj.launch.assert_called_once_with()


def test_DeleteSource_from_source_menu_when_user_is_loggedout(mocker):
    mock_source = mocker.MagicMock()
    mock_controller = mocker.MagicMock(logic.Client)
    mock_controller.api = None
    mock_delete_source_message_box_obj = mocker.MagicMock()
    mock_delete_source_message_box = mocker.MagicMock()
    mock_delete_source_message_box.return_value = (
        mock_delete_source_message_box_obj
    )

    with mocker.patch(
        'securedrop_client.gui.widgets.DeleteSourceMessageBox',
        mock_delete_source_message_box
    ):
        source_menu = SourceMenu(mock_source, mock_controller)
        source_menu.actions()[0].trigger()
        mock_delete_source_message_box_obj.launch.assert_not_called()


def test_DeleteSource_from_source_widget_when_user_is_loggedout(mocker):
    mock_source = mocker.MagicMock()
    mock_controller = mocker.MagicMock(logic.Client)
    mock_controller.api = None
    mock_event = mocker.MagicMock()
    mock_delete_source_message_box_obj = mocker.MagicMock()
    mock_delete_source_message_box = mocker.MagicMock()
    mock_delete_source_message_box.return_value = (
        mock_delete_source_message_box_obj
    )

    with mocker.patch(
        'securedrop_client.gui.widgets.DeleteSourceMessageBox',
        mock_delete_source_message_box
    ):
        source_widget = SourceWidget(None, mock_source)
        source_widget.setup(mock_controller)
        source_widget.delete_source(mock_event)
        mock_delete_source_message_box_obj.launch.assert_not_called()
