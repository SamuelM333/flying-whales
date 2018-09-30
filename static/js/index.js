_filter = function (value, containers) {
    if (!value) {
        containers.removeClass("hide");
        return;
    }
    for (let container of containers) {
        let id = container["id"];
        let container_object = $("#" + id + ".docker-container");
        id.includes(value) ? container_object.removeClass("hide") : container_object.addClass("hide");
    }
};

$("#container_search").on('change keyup paste', function () {
    let containers = $("#all .docker-container");
    let value = this.value.trim();
    _filter(value, containers);
});

$("#running_container_search").on('change keyup paste', function () {
    let containers = $("#running .docker-container");
    let value = this.value.trim();
    _filter(value, containers);
});

$("#stopped_container_search").on('change keyup paste', function () {
    let containers = $("#stopped .docker-container");
    let value = this.value.trim();
    _filter(value, containers);
});