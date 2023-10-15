from items import Course

COLLECTED_COURSES: list[Course] = []


class InMemoryCollectorPipeline:
    def process_item(self, item: Course, spider):
        COLLECTED_COURSES.append(item)
