/*
req(
    api_list['get_test'],
    {
        get_data: { 'arg1': 'test1???!!' },
        method: 'GET'
    })
    .then(resp => {
        console.log("test1", resp);
    });

req(
    api_list['get_test2'],
    {
        data: { 'arg1': 'test2???!!' },
    })
    .then(resp => {
        console.log("test2", resp);
    });

preq(
    api_list['get_test3'],
    { 'val': 'test3?2123' },
    {
        method: 'GET'
    })
    .then(resp => {
        console.log("test3", resp);
    });


preq(
    api_list['get_test4'],
    { 'val': 'test4?2123' },
    {
        get_data: { 'arg1': 'test4???!!' },
        data: { 'arg1': 'test4???!!' },
    })
    .then(resp => {
        console.log("test4", resp);
    });

*/
