import numpy as np
from bokeh.layouts import row, column
from bokeh.models.annotations import Title
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Slider
from bokeh.models.widgets.markups import Div
from bokeh.plotting import figure, show, curdoc


class LeastSquaresVisualisation:
    """This class visualizes the method of least squares fitting for a given data set. The polynomial degree can be
    varied by the user."""

    def __init__(self, x, y, max_degree):
        self.data_source = ColumnDataSource(dict(x=x, y=y))
        self.polynomial_source = ColumnDataSource(dict(x=np.linspace(0, 10, 100), y=[0] * 100))
        self.error = [0] * len(x)
        self.error_source = ColumnDataSource(dict(x=[1], single_error=[0], total_error=[0]))
        self.max_degree = max_degree
        self.title = Title()

        layout = self.create_layout()
        self.update_slider('value', 1, 1)
        curdoc().add_root(layout)
        curdoc().title = "Least Squares Fitting"
        show(layout)

    def create_layout(self):
        """This function creates the layout and sets up necessary callbacks for the interactive visualization."""
        text = Div(text='<h1>Least Squares Fitting</h1> With increasing polynomial degree the sum of squared errors '
                        'decreases. However, the increased complexity of the model may result in overfitting.',
                   width=550)
        degree_slider = Slider(title='Polynomial degree', value=1, start=1, end=self.max_degree, step=1)
        degree_slider.on_change('value', lambda attr, old, new: self.update_slider(attr, old, new))
        # data plot
        data_plot = figure(plot_width=400, plot_height=400, tools='tap', toolbar_location=None, title='',
                           x_range=(min(self.data_source.data['x']) - 1, max(self.data_source.data['x']) + 1),
                           y_range=(min(self.data_source.data['y']) - 5, max(self.data_source.data['y']) + 5))
        self.title = data_plot.title
        circles = data_plot.circle('x', 'y', source=self.data_source, size=10, color='navy', alpha=0.7)
        circles.data_source.on_change('selected', lambda attr, old, new: self.update_selection(attr, old, new))
        data_plot.line('x', 'y', source=self.polynomial_source, color='navy')
        # error plot
        _, max_error, _, _, _ = np.polyfit(self.data_source.data['x'], self.data_source.data['y'], 1, full=True)
        error_plot = figure(title='Squared Error', plot_width=150, plot_height=400, x_range=(0, 2),
                            y_range=(0, max_error[0] + 3), toolbar_location=None, x_axis_location=None, min_border_left=50)
        error_plot.xgrid.grid_line_color = None
        error_plot.ygrid.grid_line_color = None
        error_plot.vbar(x='x', top='total_error', source=self.error_source, width=1, color='navy', alpha=0.3)
        error_plot.vbar(x='x', top='single_error', source=self.error_source, width=1, color='navy', alpha=0.6)

        layout = column(text, degree_slider, row(data_plot, error_plot))
        return layout

    def set_plot_title(self, coeffs):
        """Given the coefficients of a polynomial, this function sets the representation of this polynomial function
        as title of the data plot."""
        str = ''
        rounded_coeffs = np.round(coeffs, 2)
        for coeff, power in zip(rounded_coeffs, range(len(rounded_coeffs) - 1, -1, -1)):
            str += ' + {}*x^{}'.format(coeff, power)
        str = str.replace('+ -', '- ')
        str = str.replace('*x^0', '')
        str = str.replace(' 1*', ' ')
        str = str.replace('x^1 ', 'x ')
        # remove initial +
        if str[0:3] == ' + ':
            str = str[3:]
        # fix spaces for initial -
        if str[0:3] == ' - ':
            str = '-' + str[3:]
        self.title.text = str

    def update_slider(self, attr, old, new):
        """This function updates the data and error plot when the polynomial degree is changed by the user."""
        coeffs = np.polyfit(self.data_source.data['x'], self.data_source.data['y'], new)
        # update data plot
        self.set_plot_title(coeffs)
        polynomial = np.poly1d(coeffs)
        self.polynomial_source.data['y'] = polynomial(self.polynomial_source.data['x'])
        # update error plot
        self.error = [(polynomial(x) - y)**2 for x, y in zip(self.data_source.data['x'], self.data_source.data['y'])]
        self.error_source.data['total_error'] = [sum(self.error)]
        self.update_selection('selected', self.data_source.selected, self.data_source.selected)

    def update_selection(self, attr, old, new):
        """This function updates the data and error plot when a single data point is selected by the user."""
        inds = np.array(new['1d']['indices'])
        if len(inds) == 0 or len(inds) == len(x):
            self.error_source.data['single_error'] = self.error_source.data['total_error']
        else:
            self.error_source.data['single_error'] = [sum([self.error[i] for i in inds])]

x = [1, 3, 4, 7, 9]
y = [1, 6, 1, 8, 20]

LeastSquaresVisualisation(x, y, 4)
