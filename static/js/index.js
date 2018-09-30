$("#container_search").on('change keyup paste', function () {
    let containers = $(".docker-container");
    let value = this.value.trim();

    if (!value) {
        containers.removeClass("hide");
        return;
    }
    for (let container of containers) {
        let id = container["id"];
        let container_object = $("#" + id + ".docker-container");
        id.includes(value) ? container_object.removeClass("hide") : container_object.addClass("hide");
    }
});