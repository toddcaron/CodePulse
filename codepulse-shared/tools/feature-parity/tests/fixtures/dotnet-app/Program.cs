var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/users", () => Results.Ok());
app.Run();