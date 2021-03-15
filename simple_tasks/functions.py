from calendar import LocaleHTMLCalendar


def Num2Month(month):
    if 1 == month:
        return "Enero"
    elif 2 == month:
        return "Febrero"
    elif 3 == month:
        return "Marzo"
    elif 4 == month:
        return "Abril"
    elif 5 == month:
        return "Mayo"
    elif 6 == month:
        return "Junio"
    elif 7 == month:
        return "Julio"
    elif 8 == month:
        return "Agosto"
    elif 9 == month:
        return "Septiembre"
    elif 10 == month:
        return "Octubre"
    elif 11 == month:
        return "Noviembre"
    elif 12 == month:
        return "Diciembre"
    return ""


def NextMonthYear(year, month):
    next = {
        'year': year,
        'month': month + 1,
    }
    if 13 == next['month']:
        next['month'] = 1
        next['year'] += 1
    return next


def PrevMonthYear(year, month):
    prev = {
        'year': year,
        'month': month - 1,
    }
    if 0 == prev['month']:
        prev['month'] = 12
        prev['year'] -= 1
    return prev


class TaskCalendar(LocaleHTMLCalendar):
    tasks = []

    def __init__(self, tareas = []):
        super(TaskCalendar, self).__init__(locale='')
        self.tasks = tareas

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday day">&nbsp;</td>'
        content = ""
        for task in self.tasks:
            if (task.fecha_limite.day == day
                    and task.fecha_limite.month == self.month):
                content += f'<div class="task" data-id="{task.pk}">'
                content += task
                content += '</div>'
        content = f'<div class="task-list">{content}</div>'
        content = f'<div class="day-lbl">{day}</div>{content}'
        return f'<td class="day" data-day="{day}">{content}</td>'

    def formatweek(self, theweek):
        days = "".join(self.formatday(d, wd) for (d, wd) in theweek)
        return f'<tr class="week">{days}</tr>'

    def formatweekheader(self):
        days = "".join(self.formatweekday(i) for i in self.iterweekdays())
        return f'<tr class="weekheader">{days}</tr>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        return ""
