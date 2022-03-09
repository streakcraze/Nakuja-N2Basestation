document.addEventListener('DOMContentLoaded', event => {
    //calling API (iframe Chart, fire/stop ignition)
    const baseUrl = "127.0.0.1:5000/api";

    //ignition status
    const ignitionStatus = document.getElementById('ignitionStatus');

    //starting/stopping ignition
    const startIgnition = document.getElementById("startIgnitionBtn");
    startIgnition.addEventListener('click', async () => {
        const res = await fetch(`${baseUrl}/start_ignition`, {
            method: 'POST',
        });
        if (res.status === 200) {
            let res = await fetch(`${baseUrl}/start_logging`, );
            console.log("data logs fetched", res);
        }
        ignitionStatus.innerHTML = "Ignition Started";
    });

    const stopIgnition = document.getElementById("stopIgnitionBtn");
    stopIgnition.addEventListener('click', async () => {
        const res = await fetch(`${baseUrl}/stop_ignition`, {
            method: 'POST',
        });
        if (res.status === 200) {
            let res = await fetch(`${baseUrl}/stop_logging`);
            console.log("stopped logging");
        }
        ignitionStatus.innerHTML = "Ignition stopped";
    });

    //for the logs here 

    //add iframe chart here 

});

/* TODO 
 * Change styles with change in ignition status  
 * starting logging should be done in the backend when ignition starts/stops
 * add chart
*/