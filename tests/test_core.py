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
        exc = Exception()
        task = create_task(error=Mock(return_value=exc))
        self.session._register_task(task)
        self.session.close = Mock()

        with self.session as s:
            self.assertEquals(self.session, s)
        # task is finished
        task.wait.assert_called_once_with(raise_if_error=False)
        # close has been called
        self.session.close.assert_called_once_with()
