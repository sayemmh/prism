from prism.task import PrismTask
import prism.target as PrismTarget

class Module05(PrismTask):

    def run(self, psm):
        return psm.mod('module01.py') + "This is module 05. "


# EOF