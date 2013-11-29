alter table holiday_song add column search_content tsvector;
create index holiday_song_search_content on holiday_song using gin (search_content);
