'''Example of using the Mri-client via Python, for example to use with Theano or other Python learning toolkits'''
from Mri.dispatch import MriServerDispatch
from Mri.event import TrainingEvent
import time

# The CREDS.py file should contain the server info. Don't check the CREDS.py into source control unless you want the
# server information to be public to all users of your source code
from CREDS import SERVER_ADDR, USER, PASS


def main():
    # Create the MriServer
    # The task needs a name and id at minimum. The id MUST be unique or your plots will be messed up. 
    # The name doesn't have to be unique but you'll want it to be anyway.
    task = {'name': 'Example Bindings', 'id': '001'}
    # Dispatch is setup with information about the server and the current task
    dispatch = MriServerDispatch(task, SERVER_ADDR, USER, PASS)
    # Now we have to call `setup_display` to create the report and visualization on the server.
    # We specify which value is the x-axis, and all of the attributes that we'll send along (including
    # the x-axis variable). Without this the server won't know how to properly display to the user, since
    # different training schemes use different x-axis values (ie iteration, epoch, etc) and different
    # y-axis values (ie training loss, test loss, training accuracy, etc)
    dispatch.setup_display('iteration', ['iteration', 'loss', 'accuracy'])

    for i in range(1, 10):
        # Training events specified via dictionary
        training_data = {'iteration': i, 'loss': -i, 'accuracy': i/10.0}
        # We must also specify which value is the time axis (ie iteration, epoch, etc)
        event = TrainingEvent(training_data, 'iteration')
        # Call upon the dispatch to send the event to the server
        print('Sending event {} to server'.format(event))
        dispatch.train_event(event)
        # Wait a little until next time
        time.sleep(1)

if __name__ == "__main__":
    main()
