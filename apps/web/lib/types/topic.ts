export type TopicRead = {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  order_index: number;
  parent_topic_id: number | null;
};

export type TopicWithSubtopics = TopicRead & {
  subtopics: TopicRead[];
};
