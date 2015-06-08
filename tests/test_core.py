import unittest
from mock import Mock

from rcontrol import core


def create_task(**kwargs):
    return Mock(spec=core.Task, **kwargs)


class TestBaseSession(unittest.TestCase):
    def setUp(self):
        self.session = core.BaseSession()

    def test_register_task(self):
        self.assertEquals(self.session.tasks(), [])

        task = create_task()
        self.session._register_task(task)
        self.assertEquals(self.session.tasks(), [task])

        self.session._unregister_task(task)
        self.assertEquals(self.session.tasks(), [])

        # trying to remove a non registered task is ok (is that helpful ?)
        self.session._unregister_task(task)
        self.assertEquals(self.session.tasks(), [])

    def test_wait_for_tasks(self):
        task = create_task(error=Mock(return_value=None))
        self.session._register_task(task)

        task2 = create_task(error=Mock(return_value=None))
        self.session._register_task(task2)

        self.assertEquals(self.session.wait_for_tasks(), [])

        task.wait.assert_called_once_with(raise_if_error=False)
        task2.wait.assert_called_once_with(raise_if_error=False)

    def test_wait_for_tasks_with_errors(self):
        exc1, exc2 = Exception(), Exception()
        task = create_task(error=Mock(return_value=exc1))
        self.session._register_task(task)

        task2 = create_task(error=Mock(return_value=exc2))
        self.session._register_task(task2)

        with self.assertRaises(core.TaskErrors) as cm:
            self.session.wait_for_tasks()
        self.assertEquals(cm.exception.errors, [exc1, exc2])

    def test_wait_for_tasks_with_errors_no_raise(self):
        exc1, exc2 = Exception(), Exception()
        task = create_task(error=Mock(return_value=exc1))
        self.session._register_task(task)

        task2 = create_task(error=Mock(return_value=exc2))
        self.session._register_task(task2)

        self.assertEquals(self.session.wait_for_tasks(raise_if_error=False),
                          [exc1, exc2])

    def test_with_context(self):
        task = create_task(error=Mock(return_value=None))
        self.session._register_task(task)
        self.session.close = Mock()

        with self.session as s:
            self.assertEquals(self.session, s)
        # task is finished
        task.wait.assert_called_once_with(raise_if_error=False)
        # close has been called
        self.session.close.assert_called_once_with()

    def test_task_errors_with_context(self):
        exc = Exception()
        task = create_task(error=Mock(return_value=exc))
        self.session._register_task(task)
        self.session.close = Mock()

        with self.assertRaises(core.TaskErrors) as cm:
            with self.session as s:
                self.assertEquals(self.session, s)

        # task is finished
        task.wait.assert_called_once_with(raise_if_error=False)
        # close has been called
        self.session.close.assert_called_once_with()
        # got a task error at the end
        self.assertEquals(cm.exception.errors, [exc])

    def test_exception_with_context(self):
        exc = Exception()
        task = create_task(error=Mock(return_value=exc))
        self.session._register_task(task)
        self.session.close = Mock()

        class MyException(Exception):
            pass

        # here TaskErrors is not raised since we had an exception
        # in the with statement. There should be only a print that
        # notify user from the failure. [TODO test this]
        with self.assertRaises(MyException):
            with self.session:
                raise MyException()

        # task is finished
        task.wait.assert_called_once_with(raise_if_error=False)
        # close has been called
        self.session.close.assert_called_once_with()


def create_session(**kwargs):
    return Mock(spec=core.BaseSession, **kwargs)


class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.sessions = core.SessionManager()

    def test_set_attr(self):
        session = core.BaseSession()
        self.sessions.local = session
        self.assertEqual(self.sessions, {'local': session})
        # test getattr
        self.assertEqual(session, self.sessions.local)

    def test_delattr(self):
        self.sessions.local = core.BaseSession()
        del self.sessions.local
        self.assertEqual(self.sessions, {})
        with self.assertRaises(AttributeError):
            self.sessions.local

    def test_any_attr_can_be_attached(self):
        self.sessions.foo = 'bar'
        self.assertEqual(self.sessions.foo, 'bar')
        # not stored in the OrderedDict
        self.assertEqual(self.sessions, {})
        # can be deleted
        del self.sessions.foo
        with self.assertRaises(AttributeError):
            self.sessions.foo

    def test_that_only_sessions_can_be_stored_in_dict(self):
        with self.assertRaises(TypeError):
            # must use a string as the key
            self.sessions[1] = core.BaseSession()

        with self.assertRaises(TypeError):
            # must use a BaseSession as the value
            self.sessions['local'] = 'thing'

        # nothing is stored in the dict
        self.assertEqual(self.sessions, {})

        session = core.BaseSession()
        self.sessions['local'] = session
        self.assertEqual(self.sessions, {'local': session})

    def test_wait_for_tasks(self):
        self.sessions.s1 = create_session(
            wait_for_tasks=Mock(return_value=[]))
        self.sessions.s2 = create_session(
            wait_for_tasks=Mock(return_value=[]))

        self.assertEqual(self.sessions.wait_for_tasks(), [])
        self.sessions.s1.wait_for_tasks.assert_called_with(
            raise_if_error=False)
        self.sessions.s2.wait_for_tasks.assert_called_with(
            raise_if_error=False)

    def test_wait_for_tasks_with_tasks_errors(self):
        exc1, exc2 = Exception(), Exception()
        self.sessions.s1 = create_session(
            wait_for_tasks=Mock(return_value=[exc1]))
        self.sessions.s2 = create_session(
            wait_for_tasks=Mock(return_value=[exc2]))

        # by default, this raise an exception
        with self.assertRaises(core.TaskErrors) as cm:
            self.sessions.wait_for_tasks()
        self.assertEqual(cm.exception.errors, [exc1, exc2])

        # if specified, just return the exception list
        self.assertEqual(self.sessions.wait_for_tasks(raise_if_error=False),
                         [exc1, exc2])

    def test_close(self):
        self.sessions.s1 = create_session()
        self.sessions.s2 = create_session()
        self.sessions.close()
        self.sessions.s1.close.assert_called_once_with()
        self.sessions.s2.close.assert_called_once_with()

    def test_inside_with(self):
        self.sessions.wait_for_tasks = Mock(return_value=[])
        with self.sessions as s:
            self.assertEqual(s, self.sessions)
            s.s1 = create_session(auto_close=True)
            s.s2 = create_session(auto_close=False)
        # wait_for_tasks was called
        self.sessions.wait_for_tasks.assert_called_once_with(
            raise_if_error=False)
        # s1 was closed, s2 was not
        s.s1.close.assert_called_once_with()
        self.assertEqual(len(s.s2.close.mock_calls), 0)

    def test_inside_with_with_task_errors(self):
        exc1 = Exception()
        # TaskErrors will be raised
        with self.assertRaises(core.TaskErrors):
            with self.sessions as s:
                self.assertEqual(s, self.sessions)
                s.s1 = create_session(
                    wait_for_tasks=Mock(return_value=[exc1]),
                    auto_close=True,
                )

    def test_inside_with_with_errors(self):
        exc1 = Exception()
        # KeyboardInterrupt will be raised instead of TaskErrors
        with self.assertRaises(KeyboardInterrupt):
            with self.sessions as s:
                self.assertEqual(s, self.sessions)
                s.s1 = create_session(
                    wait_for_tasks=Mock(return_value=[exc1]),
                    auto_close=True,
                )
                raise KeyboardInterrupt
