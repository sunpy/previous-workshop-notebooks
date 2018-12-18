#!/usr/bin/env python
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys
from sunpy.lightcurve import GOESLightCurve
from sunpy.time import TimeRange
from datetime import datetime, timedelta

DEFAULT_TR = TimeRange('2012/07/21', '2012/07/22')


class GOESGui(QtGui.QMainWindow):
    """
    A GUI.
    """

    def __init__(self):#, filename = None):
        #initialize a viewer window with a grid layout.
        #----------------------------------------------
        #----------------------------------------------
        super(QtGui.QMainWindow,self).__init__()
        self.ax0 = None

        self.resize(500, 500)
        self.setWindowTitle('GOES')

        # Top GroupBox
        myQWidget = QtGui.QWidget()
        myBoxLayout = QtGui.QVBoxLayout()
        myQWidget.setLayout(myBoxLayout)
        self.setCentralWidget(myQWidget)

        self.tr = DEFAULT_TR
        self.lc = GOESLightCurve.create(self.tr)

        # date edit box
        self.dateSet = QtGui.QDateTimeEdit()
        self.dateSet.setDateTime(QtCore.QDateTime(QtCore.QDate(DEFAULT_TR.start.year, DEFAULT_TR.start.month, DEFAULT_TR.start.day), QtCore.QTime(00, 00, 00)))
        self.dateSet.setCalendarPopup(True)
        self.dateSet.setDisplayFormat("yyyy/MM/dd HH:mm:ss UT")
        myBoxLayout.addWidget(self.dateSet)

        # create the plot
        self.fig0 = plt.figure()
        self.canvas0 = FigureCanvas(self.fig0)
        self.update()
        myBoxLayout.addWidget(self.canvas0)

        # the next day button
        nextDayButton = QtGui.QPushButton('Next Day')
        myBoxLayout.addWidget(nextDayButton)
        QtCore.QObject.connect(nextDayButton, QtCore.SIGNAL('clicked()'), self.update_next_tr)

        # the previous day button
        previousDayButton = QtGui.QPushButton('Previous Day')
        myBoxLayout.addWidget(previousDayButton)
        QtCore.QObject.connect(previousDayButton, QtCore.SIGNAL('clicked()'), self.update_prev_tr)

        # refresh button
        refreshButton = QtGui.QPushButton('Refresh')
        myBoxLayout.addWidget(refreshButton)
        QtCore.QObject.connect(refreshButton, QtCore.SIGNAL('clicked()'), self.refresh)

        self.show()

    def update(self):
        # update the date edit box
        self.dateSet.setDateTime(QtCore.QDateTime(QtCore.QDate(self.tr.start.year, self.tr.start.month, self.tr.start.day), QtCore.QTime(00, 00, 00)))

        # next update the plot
        # clear the plot if it exists
        if self.ax0 is not None:
            self.ax0.cla()

        # now create the matplotlib plot
        self.ax0 = self.fig0.add_subplot(1, 1, 1)
        self.ax0.plot(self.lc.data.index, self.lc.data['xrsa'], color='red')
        self.ax0.plot(self.lc.data.index, self.lc.data['xrsb'], color='blue')
        self.ax0.set_xlabel(str(self.tr.start))
        self.ax0.set_yscale('log')
        self.ax0.set_ylim(1e-9, 1e-2)
        self.ax0.set_ylabel('Watts m$^{-2}$')
        self.ax0.tick_params(axis='both', labelsize=9)
        self.fig0.autofmt_xdate()

        # now draw it
        self.fig0.canvas.draw()

    def update_next_tr(self):
        self.tr = self.tr.next()
        self.lc = GOESLightCurve.create(self.tr)
        self.update()

    def update_prev_tr(self):
        self.tr = self.tr.previous()
        self.lc = GOESLightCurve.create(self.tr)
        self.update()

    def refresh(self):
        date = self.dateSet.date()
        start_date = datetime(date.year(), date.month(), date.day())
        self.tr = TimeRange(start_date, start_date + timedelta(days=1) )
        self.lc = GOESLightCurve.create(self.tr)
        self.update()

def main():
    app = QtGui.QApplication(sys.argv)
    ex = GOESGui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
